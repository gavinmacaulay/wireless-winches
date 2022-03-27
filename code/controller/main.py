# Code to run on the Aqualyd echosounder calibration winch wireless control box

import machine
import utime
import xbee
import sys

# callback for when data is received from the winches
def receive_status(m):
    if m is None: # no new message
        pass
    else:
        # pull out the message from the received data
        status = m['payload'].decode('ascii')
        
    # goes out on the UART
    print(status)

# Pin definitions
winch1out = machine.Pin(machine.Pin.board.D10, machine.Pin.IN, machine.Pin.PULL_UP)
winch1in = machine.Pin(machine.Pin.board.D12, machine.Pin.IN, machine.Pin.PULL_UP)

winch2out = machine.Pin(machine.Pin.board.D1, machine.Pin.IN, machine.Pin.PULL_UP) # D18
winch2in = machine.Pin(machine.Pin.board.D11, machine.Pin.IN, machine.Pin.PULL_UP) # D16

winch3out = machine.Pin(machine.Pin.board.D2, machine.Pin.IN, machine.Pin.PULL_UP)
winch3in = machine.Pin(machine.Pin.board.D3, machine.Pin.IN, machine.Pin.PULL_UP)

speedPot = machine.ADC(machine.Pin.board.D0)

led = machine.Pin(machine.Pin.board.D4, machine.Pin.OUT)
ledState = False

# Time between checking controls (also the time between sending messages to the winches)
pollInterval = 100 # [ms] 

# Codes that are sent to the receivers
stop = '0'
up = '2'
down = '1'

xbee.receive_callback(receive_status)

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

            # Get speed from the potentiometer
            speed = speedPot.read()

            # The ADC is 12 bit, but we only want 8 bits to send to the winches,
            # so chop off the lower bits (and it removes ADC noise too)                
            s += '{:03d}'.format(speed >> 4)
            
            #print(s)
            
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
    
