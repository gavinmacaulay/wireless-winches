# Code to run on the Aqualyd echosounder calibration winches

# TODO
# - output debugging on bluetooth - need to detect if bluetooth connection exists
#     before trying to send data
# - get_variables() doesn't yet work

import xbee
import array
from sys import stdin, stdout

class TicXbee(object):
    def __init__(self):
        # Get the winch id
        self.addr = int(xbee.atcmd('NI')[-1])
    
    def send_command(self, cmd, data_bytes):
        # data_byes should be an iterable data structure
        
        buf = bytearray([cmd])
        if data_bytes:
            buf.extend(bytes(data_bytes))
         
        stdout.buffer.write(buf)
        #relay.send(relay.BLUETOOTH, 'Sent {} bytes to Tic.'.format(len(buf)))
   
    def get_variables(self, offset, length):
        self.send_command(0xA1, [offset, length])
        result = stdin.buffer.read(length)
        if len(result) != length:
            pass
            #relay.send(relay.BLUETOOTH, "Expected to read {} bytes, got {}.".format(length, len(result)))
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


# Given the parameters of the reel and motor, work out step rate needed to get
# the desired line speed range.
min_line_speed = 0.1 # [m/s]
max_line_speed = 1.0 # [m/s]

drum_diameter = 0.070 # [m] 
gearbox_ratio = 4.25 # the PG4 gearbox
rotation_per_step = 1.8 # [deg] before gearbox
substep_divider = 0.25 # setting in the motor driver 
tic_multiplier = 10000.0 # the tic wants pulse rates to be multiplied by this
speed_steps = 256 # the number of different speeds to offer

drum_circum = 3.14159 * drum_diameter # [m]
tic_pulses_per_rev = 360.0/rotation_per_step * gearbox_ratio / substep_divider * tic_multiplier

min_tic_pulses = min_line_speed / drum_circum * tic_pulses_per_rev
max_tic_pulses = max_line_speed / drum_circum * tic_pulses_per_rev

# note: there are some speeds that the motor resonates strongly at and for which
# the motor 'jams'. These ranges need to be avoided...
step_tic_pulses = (max_tic_pulses - min_tic_pulses) / (speed_steps-1)

# speed as a signed 32 bit integer. Use array instead of list, 
# for efficiency (as per micropython guidelines)
speed = array.array('l', [int(i*step_tic_pulses + min_tic_pulses) for i in range(0,speed_steps)])

step_mode = 0 # full step

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

# Listen for wireless commands.
while True:
    m = xbee.receive() # this does not block
    if m is None: # no new message
        pass
    else:
        # pull out the message from the received data
        cmd = m['payload'].decode('ascii')

        # parse out the speed from the payload
        speed_num = int(cmd[3:6]) # 0-255

        #relay.send(relay.BLUETOOTH, cmd)
        
        # and then the direction, to give velocity
        dir_char = cmd[winch-1]
        if dir_char == '1': # pay out
            velocity = speed[speed_num]
        elif dir_char == '2': # haul in
            velocity = -speed[speed_num]
        else: # '0' or anything else
            velocity = 0 # stop

        #print(cmd + ' ' + str(velocity))

        # Send to the Tic
        tic.energize()
        tic.exit_safe_start()
        tic.reset_command_timeout()
        tic.set_velocity(velocity, step_mode)
