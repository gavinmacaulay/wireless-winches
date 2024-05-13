# Code to run on the Aqualyd echosounder calibration winches

import xbee
import array
from sys import stdin, stdout
from machine import Pin
from micropython import kbd_intr
from store_value import storeValue

class TicXbee(object):
    def __init__(self):
        # Get the winch id
        self.addr = int(xbee.atcmd('NI')[-1])
        kbd_intr(-1) # ignore Ctrl-C (0x03) on UART
    
    def send_command(self, cmd, data_bytes):
        # data_byes should be an iterable data structure
        
        buf = bytearray([cmd])
        if data_bytes:
            buf.extend(bytes(data_bytes))
         
        stdout.buffer.write(buf)
   
    def get_variables(self, offset, length):
        self.send_command(0xA1, [offset, length])

        result = stdin.buffer.read(length)

        if result is None:
            result = []

        return bytearray(result) 
   
    def set_velocity(self, velocity, step_mode):
        #relay.send(relay.BLUETOOTH, 'Setting velocity to {}, stepping to {}'.format(velocity, step_mode))
        # A 32-bit write for the velocity
        self.send_command(0xE3, [((velocity >>  7) & 1) | ((velocity >> 14) & 2) |
                                 ((velocity >> 21) & 4) | ((velocity >> 28) & 8),
                                 velocity >> 0 & 0x7F,
                                 velocity >> 8 & 0x7F,
                                 velocity >> 16 & 0x7F,
                                 velocity >> 24 & 0x7F]) 
        # A 7-bit write for the stepping
        self.send_command(0x94, [step_mode & 127]) 

    def set_current_limit(self, current):
        # A 7-bit write for the current
        current_value = int(current / 40)
        self.send_command(0x91, [current_value & 127])
        
    def get_serial_device_number(self):
        n = self.get_variables(0x07, 1)
        return n

    def reset_command_timeout(self):
        #relay.send(relay.BLUETOOTH, 'Sent reset_command_timeout')
        self.send_command(0x8C, [])

    def exit_safe_start(self):
        #relay.send(relay.BLUETOOTH, 'Sent exit_safe_start')
        self.send_command(0x83, [])

    def energize(self):
        self.send_command(0x85, [])

def twos_complement(value, bitWidth):

    if value >= 2**bitWidth:
        return value # should raise an exception
    else:
        return value - int((value << 1) & 2**bitWidth)

def get_status():
    # Get input voltage
    vin_bytes = tic.get_variables(0x33, 2) # [mV], unsigned 16-bit
    vin = int.from_bytes(vin_bytes, 'little') / 1000
    
    # Get position & velocity
    state = tic.get_variables(0x22, 8) # 2 x signed 32-bit
    
    position = int.from_bytes(state[0:4], 'little') # microsteps
    position = -1 * twos_complement(position, 32)
    
    velocity = int.from_bytes(state[4:8], 'little') # microsteps per 10000s
    velocity = -1 * twos_complement(velocity, 32)
        
    # Get Xbee internal temperature
    xbee_temp = int(xbee.atcmd('TP')) # 2's complement
    if xbee_temp > 0x7FFF:
        xbee_temp = xbee_temp - 0x10000
        
    return (vin, position, velocity, xbee_temp)

# Config variables
status_period = 5 # generate a status message every x recieved messages from controller
max_motor_current = 2720 # [mA] From motor specs

# Reduce the max allowed motor current when winch is stopped. This significantly
# reduces the power used during a calibration.
current_limit_stationary = 1000 # [mA]

# Given the parameters of the reel and motor, work out step rate needed to get
# the desired line speed range.
min_line_speed = 0.02 # [m/s]
max_line_speed = 1.0 # [m/s]

drum_diameter = 0.070 # [m] 
gearbox_ratio = 4.25 # the PG4 gearbox
rotation_per_step = 1.8 # [deg] before gearbox
substep_divider = 0.25 # setting in the motor driver 
tic_multiplier = 10000.0 # the tic wants pulse rates to be multiplied by this
speed_steps = 256 # the number of different speeds to offer

step_mode = 2 # 1/4 step

drum_circum = 3.14159 * drum_diameter # [m]
tic_pulses_per_rev = 360.0/rotation_per_step * gearbox_ratio / substep_divider * tic_multiplier

min_tic_pulses = min_line_speed / drum_circum * tic_pulses_per_rev
max_tic_pulses = max_line_speed / drum_circum * tic_pulses_per_rev

# Use to convert pulses/s and position ticks to m/s and m
pulses_factor_speed = drum_circum / tic_pulses_per_rev
pulses_factor_position = drum_circum / tic_pulses_per_rev * tic_multiplier

pos_offset = 0.0 # [m]
try:
    pos_store = storeValue()
    pos_offset = pos_store.get()
except RuntimeError:
    pos_offset = 0.0 # [m]

# note: there are some speeds that the motor resonates strongly at and for which
# the motor 'jams'. These ranges need to be avoided...
step_tic_pulses = (max_tic_pulses - min_tic_pulses) / (speed_steps-1)

# speed as a signed 32 bit integer. Use array instead of list, 
# for efficiency (as per micropython guidelines)
speed = array.array('l', [int(i*step_tic_pulses + min_tic_pulses) for i in range(0,speed_steps)])

led = Pin(Pin.board.D10, Pin.OUT)
max_payload_len = int(xbee.atcmd('NP')) # for sending over the air

tic = TicXbee()

# and an index into the received messages.
winch = tic.addr # (1, 2, or 3)

# get the motor controller started
tic.energize()
tic.exit_safe_start()

# The micropython receive buffer needs to be emptied before we start processing
# messages, but there is no flush() or similar call. 
# The buffer can only hold 4 packets, so just read it 4 times quickly.
for _ in range(4):
    xbee.receive()

status_counter = 0
prev_current_limit = 0
velocity_actual = None

# Listen for wireless commands.
while True:
    m = xbee.receive() # this does not block
    if m is None: # no new message
        pass
    else:
        status_counter += 1
        # get the address of the sender
        sender_addr = m['sender_eui64']

        # pull out the message from the received data
        cmd = m['payload'].decode('ascii')

        # parse out the speed from the payload
        speed_num = int(cmd[3:6]) # 0-255

        #relay.send(relay.BLUETOOTH, cmd)
        
        # and then the direction, to give velocity
        dir_char = cmd[winch-1]
        if dir_char == '1': # pay out
            velocity_req = speed[speed_num]
        elif dir_char == '2': # haul in
            velocity_req = -speed[speed_num]
        else: # '0' or anything else
            velocity_req = 0 # stop

        # Send to the Tic
        tic.energize()
        tic.exit_safe_start()
        tic.reset_command_timeout()

        # To reduce power usage, limit the motor current when the winch is
        # stationary. Only do this when the motor is actually stationary, and 
        # when going from stationary to moving, increase the current before
        # moving the motor.

        if (velocity_req == 0) and (velocity_actual == 0):
            current_limit = current_limit_stationary
        else:
            current_limit = max_motor_current
         
        # change the tic current limit if it is different to last time
        if prev_current_limit != current_limit:
            tic.set_current_limit(current_limit)
            prev_current_limit = current_limit

        # once the current limit is adjusted (if necessary), change the 
        # requested velocity
        tic.set_velocity(velocity_req, step_mode)

        # get and send a status message to the controller
        if status_counter >= status_period:
            status_counter = 0

            (vin, pos_actual, velocity_actual, t) = get_status()
            v_physical = velocity_actual * pulses_factor_speed # [m/s]
            p_physical = pos_actual * pulses_factor_position + pos_offset # [m]
            try:
                pos_store.put(p_physical)
            except Exception as e:
                pass
            
            data = '{},{:.1f},{},{:.2f},{:.2f}'.format(winch, vin, t, p_physical, v_physical)
            if len(data) > max_payload_len:
                data = '{},error - message too long'.format(winch)
        
            # send to whoever sent the most recent message we received
            try:
                led.value(True)
                xbee.transmit(sender_addr, data)
                led.value(False)
            except Exception as e:
                pass


        
        
        
        
        
        
