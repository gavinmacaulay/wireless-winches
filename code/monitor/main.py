"""Code to run on an Aqualyd winch monitoring device (an Xbee3)."""

from sys import stdout
import time
import xbee
import machine

led = machine.Pin(machine.Pin.board.D4, machine.Pin.OUT)
led(0)

# Time between adbvertising that we are here
advertiseInterval = 1000  # [ms]


def receive_status(m):
    """Is called when data is received from the winches and controllers."""
    if m is None:  # no new message
        return

    # we only want to output messages addressed to us, so ignore broadcast ones
    if m['broadcast']:
        return

    # pull out the message from the received data
    status = m['payload'].decode('ascii')

    # and send out via the serial port
    try:
        led(1)
        stdout.write(status+'\n')
        led(0)
    except Exception:
        pass

while True:
    try:
        xbee.receive_callback(receive_status)

        while True:
            # Tell others we are here
            xbee.transmit(xbee.ADDR_BROADCAST, 'MONITOR')
            time.sleep_ms(advertiseInterval)
    except Exception as e:
        print('An error occurred: {} = {}'.format(type(e).__name__, e))
        print('Waiting a bit and trying again...')
        time.sleep(2)
    