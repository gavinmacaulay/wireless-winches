# Code to run on the Aqualyd echosounder calibration winch wireless control box

import machine
import utime
import xbee
import sys

# Pin definitions
winch1out = machine.Pin(machine.Pin.board.D5, machine.Pin.IN, machine.Pin.PULL_UP)
winch1in = machine.Pin(machine.Pin.board.D10, machine.Pin.IN, machine.Pin.PULL_UP)

winch2out = machine.Pin(machine.Pin.board.D3, machine.Pin.IN, machine.Pin.PULL_UP)
winch2in = machine.Pin(machine.Pin.board.D2, machine.Pin.IN, machine.Pin.PULL_UP)

winch3out = machine.Pin(machine.Pin.board.D11, machine.Pin.IN, machine.Pin.PULL_UP)
winch3in = machine.Pin(machine.Pin.board.D1, machine.Pin.IN, machine.Pin.PULL_UP)

speedBit0 = machine.Pin(machine.Pin.board.D12, machine.Pin.IN, machine.Pin.PULL_UP)
speedBit1 = machine.Pin(machine.Pin.board.D9, machine.Pin.IN, machine.Pin.PULL_UP)
speedBit2 = machine.Pin(machine.Pin.board.D0, machine.Pin.IN, machine.Pin.PULL_UP)
#speedBit3 = machine.Pin(machine.Pin.board.XXX, machine.Pin.IN, machine.Pin.PULL_UP) # not used

led = machine.Pin(machine.Pin.board.D4, machine.Pin.OUT)
ledState = False

# Table to convert the binary value from the encoder into a speed value
#speed = [6, 5, 4, 3, 2, 1, 0, 7] 
#speed = [223, 191, 159, 127, 95, 63, 0, 255]
speed = [191, 159, 127, 95, 63, 31, 0, 255]

# Time between checking controls (also the time between sending messages to the winches)
pollInterval = 200 # [ms] 

# Codes that are sent to the receivers
stop = '0'
up = '2'
down = '1'

while True:
    try:
        while True:
            # Form the message that will be sent to the receivers
            s = ''
            if winch1out.value() == 0: # pulled low by a switch
                s += down
            elif winch1in.value() == 0:
                s += up
            else:
                s += stop
        
            if winch2out.value() == 0:
                s += down
            elif winch2in.value() == 0:
                s += up
            else:
                s += stop
        
            if winch3out.value() == 0:
                s += down
            elif winch3in.value() == 0:
                s += up
            else:
                s += stop
                
            encoderValue = speedBit0.value() + 2*speedBit1.value() + 4*speedBit2.value()
            #s += str(speed[encoderValue])
            s += '{:03d}'.format(speed[encoderValue])
            
            # Send to whoever is listening
            xbee.transmit(xbee.ADDR_BROADCAST, s)
            
            # Flick the LED state every time we transmit
            led.value(ledState)
            ledState = not ledState
        
            # Do nothing
            utime.sleep_ms(pollInterval)
                        
    except:
        # Will appear on the MicroPython terminal, so useful for debugging.
        print('Exception caught: ', sys.exc_info()[0])
    