"""Code to run on an Aqualyd winch monitoring device (an Xbee3)."""

import utime  # noqa
import xbee  # noqa
from sys import stdout

# Time between adbvertising that we are here
advertiseInterval = 1000  # [ms]

def receive_status(m):
    """Is called when data is received from the winches and controllers."""
    if m is None:  # no new message
        return

    # we don't want to send out the controller broadcast messages or broadcasts
    # from other monitor devices
    if m['broadcast']:
        return

    # pull out the message from the received data
    status = m['payload'].decode('ascii')

    # and send out via the serial port
    try:
        stdout.write(status+'\n')
    except Exception:  # noqa
        pass

xbee.receive_callback(receive_status)

while True:
    # Tell others we are here
    # we define cluster_i of 0x0101 as meaning not an control message
    xbee.transmit(xbee.ADDR_BROADCAST, 'MONITOR', cluster_id=0x0101)
    utime.sleep_ms(advertiseInterval)  # does this prevent the callback from happening?
