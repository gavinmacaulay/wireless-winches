"""Code to run on the Aqualyd echosounder calibration winch wireless control box."""

import machine
# Status leds. Do these early cause default states of the pin can cause unwanted
# operation of the leds
ledRed = machine.Pin(machine.Pin.board.D15, machine.Pin.OUT, value=0)
ledGreen = machine.Pin(machine.Pin.board.D19, machine.Pin.OUT, value=0)
from max17048 import max17048  # noqa
import utime  # noqa
import xbee  # noqa
from xbee import relay  # noqa
from sys import stdout

# Configurations

# Time between checking controls (also the time between sending messages to the winches)
pollInterval = 100  # [ms]

# Used to do things every x'th time through the main loop
loopCount = 0

# How often to toggle the status LED
statusToggleRate = 2  # every nth time through the main loop

# How often to measure and send the controller battery voltage
batteryInterval = 50  # times through the pollInternal loop

# Codes that are sent to the receivers
stop = '0'
up = '2'
down = '1'

# Mode switch states
EXTENDER = 0
CONTROLLER = 1
modeText = ['extender', 'controller']

# if there is no battery gauge, we say that it is empty
bVolt = 0.0  # [V]
bSOC = 0.0  # [%]
bCRate = 0.0  # [%/hr]

# This xbee's node identifier
ident = xbee.atcmd('NI')

# Battery monitoring
try:
    battery = max17048()
except:  # noqa
    battery = None


def receive_status(m):
    """Is called when data is received from the winches."""
    if m is None:  # no new message
        return

    # pull out the message from the received data
    status = m['payload'].decode('ascii')

    # and send out on Bluetooth
    try:
        relay.send(relay.BLUETOOTH, status)
    except:  # noqa
        pass

    # For receiving the messages over the controllers' serial to USB converter
    if currentMode == CONTROLLER:
        try:
            stdout.write(status+'\n')
        except:  # noqa
            pass


def send_self_battery(ident, mode, v, soc, rate):
    """Send on Bluetooth and serial the state of the battery in the controller."""
    msg = '0,{},{},{:0.2f},{:0.1f},{:0.1f}'.format(ident, modeText[mode], v, soc, rate)
    try:
        relay.send(relay.BLUETOOTH, msg)
    except:  # noqa
        pass

    # For receiving the messages over the controllers' serial to USB converter
    if mode == CONTROLLER:
        try:
            stdout.write(msg+'\n')
        except:  # noqa
            pass

def setStatusLED(mode):
    """Set the status LED to indicate the operation mode."""
    if mode == CONTROLLER:
        ledGreen.on()
        ledRed.off()
    elif mode == EXTENDER:
        ledGreen.off()
        ledRed.on()


def flashStatusLED(mode, state):
    """Use to flash the leds on and off."""
    if mode == CONTROLLER:
        ledGreen.value(state)

    if mode == EXTENDER:
        ledRed.value(state)


# Disable pins that aren't used.
machine.Pin(machine.Pin.board.D2, mode=machine.Pin.DISABLED)
machine.Pin(machine.Pin.board.D16, mode=machine.Pin.DISABLED)
machine.Pin(machine.Pin.board.D17, mode=machine.Pin.DISABLED)
machine.Pin(machine.Pin.board.D18, mode=machine.Pin.DISABLED)

# Mode select switch
modeSelect = machine.Pin(machine.Pin.board.D5, machine.Pin.IN, machine.Pin.PULL_UP)

# And set LEDs to reflect this value
currentMode = modeSelect.value()
setStatusLED(currentMode)

# The speed potentiometer
speedPot = machine.ADC(machine.Pin.board.D0)

# Pin definitions for the winches
winch1out = machine.Pin(machine.Pin.board.D10, machine.Pin.IN, machine.Pin.PULL_UP)
winch1in = machine.Pin(machine.Pin.board.D12, machine.Pin.IN, machine.Pin.PULL_UP)
winch2out = machine.Pin(machine.Pin.board.D7, machine.Pin.IN, machine.Pin.PULL_UP)
winch2in = machine.Pin(machine.Pin.board.D9, machine.Pin.IN, machine.Pin.PULL_UP)
winch3out = machine.Pin(machine.Pin.board.D4, machine.Pin.IN, machine.Pin.PULL_UP)
winch3in = machine.Pin(machine.Pin.board.D3, machine.Pin.IN, machine.Pin.PULL_UP)

if currentMode == CONTROLLER:
    xbee.receive_callback(receive_status)

while True:
    try:
        while True:
            # work out if we need to change mode
            if (modeSelect.value() != currentMode):
                loopCount = 0  # will cause a new battery message to be sent to the app
                if currentMode == CONTROLLER:
                    currentMode = EXTENDER
                    xbee.receive_callback(None)
                else:
                    currentMode = CONTROLLER
                    xbee.receive_callback(receive_status)

                setStatusLED(currentMode)

            if currentMode == CONTROLLER:
                # Form the message that will be sent to the receivers
                s = ''
                if winch1out.value() == 0:  # pulled low by a switch
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

                # The speed ADC is 12 bit, but we only want 8 bits to send to the winches,
                # so chop off the lower bits (and it removes ADC noise too)
                s += '{:03d}'.format(speed >> 4)

                # The app can generate control messages for the winches, so pass them on.
                app_msg = relay.receive()
                if app_msg is not None:
                    # Got something from the app
                    app_cmd = app_msg['message'].decode('ascii')
                    if len(app_cmd) == 2:
                        s += app_cmd
                else:
                    s += '00'

                # Send to whoever is listening
                xbee.transmit(xbee.ADDR_BROADCAST, s)

            # Measure battery voltage and do LEDs
            if (loopCount % batteryInterval) == 0:
                if battery is not None:
                    bVolt = battery.getVCell()  # [V]
                    bSOC = battery.getSOC()  # [%]
                    bCRate = battery.getChargeRate()  # [%/hr]
                    if bSOC > 100.0:
                        bSOC = 100.0
                send_self_battery(ident, currentMode, bVolt, bSOC, bCRate)

            # Turn on the status leds every statusToggleRate time through
            if bSOC > 50.0:
                statusToggleRate = 2  # flashes every second time through the loop
            elif bSOC > 25.0:
                statusToggleRate = 5  # every 5th time
            else:
                statusToggleRate = 10  # every 10th time

            if (loopCount % statusToggleRate) == 0:
                flashStatusLED(currentMode, True)

            loopCount += 1

            # Wait a bit (also controls how often we send messages to the winches)
            utime.sleep_ms(pollInterval)

            # Off with the LEDs
            if statusToggleRate != 1:
                flashStatusLED(currentMode, False)

    except Exception as e:
        # Will appear on the MicroPython terminal, so useful for debugging.
        print(str(e))
