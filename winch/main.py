# Code to run on the Aqualyd echosounder calibration winches

# TODO
# Implement local switching (at a fixed speed)

import machine
import xbee
import array
#from xbee import relay

class TicXbee(object):
    def __init__(self):
        self.i2c = machine.I2C(1, freq=100000)
        # Get the winch id
        #addr = self.i2c.scan()
        #self.addr = addr[0] # should only be one on the bus
        self.addr = 1
    
    def send_command(self, cmd, data_bytes):
        #
        # data_byes should be an iterable data structure
        
        buf = bytearray([cmd])
        if data_bytes:
            buf.extend(bytes(data_bytes))
            
        #print(buf)
        
        #self.i2c.writeto(self.addr<<1, buf)
   
    def set_velocity(self, velocity, step_mode):
        print('set_velocity = {}, stepping = {}'.format(velocity, step_mode))
        # A 32-bit write for the velocity
        self.send_command(0xE3, [velocity >> 0 & 0xFF,
                                 velocity >> 8 & 0xFF,
                                 velocity >> 16 & 0xFF,
                                 velocity >> 24 & 0xFF]) 
        # A 7-bit write for the stepping
        self.send_command(0x94, [step_mode & 127]) 

    def reset_command_timeout(self):
        print('reset_command_timeout')
        self.send_command(0x8C, [])

    def exit_safe_start(self):
        print('exit_safe_start')
        self.send_command(0x83, [])

# Local control switch
#winchout = machine.Pin(machine.Pin.board.D5, machine.Pin.IN, machine.Pin.PULL_UP)
#winchin = machine.Pin(machine.Pin.board.D10, machine.Pin.IN, machine.Pin.PULL_UP)

# pre-programmed Tic settings that are needed:
# - command timeout
# - max current
# - max speed
# - and others...

# Motor speeds and substep setting for the 8 speeds (0-7) that come from the control unit
# Use arrays for these instead of lists, for efficiency (as per micropython guidelines)
speed = array.array('l', [100, 1000, 10000, 100000, 500000, 1000000, 10000000, 12000000]) # signed 32 bit integer
stepping = array.array('B', [3, 3, 2, 2, 1, 0, 0, 0]) # slower speeds are to have substeps, unsigned 8-bit integer
local_speed_i = -1

# TODO: Setup baud rate of stdin/stdout
tic = TicXbee()

winch = tic.addr # (0, 1, or 2)
tic.exit_safe_start()

# The micropython receive buffer needs to be emptied before we start processing
# messages, but there is no flush() or similar call. 
# The buffer can only hold 4 packets, so just read it 4 times quickly.

for _ in range(4):
    xbee.receive()

while True:
    m = xbee.receive() # this does not block
    if m is None: # no new message, so check the local control switches
        pass
        # # Check for local control inputs
        # if winchout.value() == 0: # pulled low by a switch
        #     velocity = speed[local_speed_i]
        # elif winchin.value() == 0:
        #     velocity = speed[local_speed_i] * -1
        # else:
        #     velocity = 0
        # stepping = [-1]
    else:
        cmd = m['payload'].decode('ascii')

        # parse out the direction and speed from the payload
        speed_num = int(cmd[3]) # 0-7

        #relay.send(relay.BLUETOOTH, cmd)
        
        dir_char = cmd[winch]
        if dir_char == '0':
            velocity = 0
        elif dir_char == '1': # pay out
            velocity = speed[speed_num]
        else: # is 2 and means haul in
            velocity = -speed[speed_num]

        step_mode = stepping[speed_num]

        #print(cmd + ' ' + str(velocity) + ' ' + str(step_mode))

        # Send to the Tic
        tic.reset_command_timeout()
        tic.set_velocity(velocity, step_mode)
