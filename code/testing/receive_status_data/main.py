# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 17:28:09 2022

@author: gavin
"""


import xbee
import array
from sys import stdin, stdout
import utime

# The micropython receive buffer needs to be emptied before we start processing
# messages, but there is no flush() or similar call. 
# The buffer can only hold 4 packets, so just read it 4 times quickly.
for _ in range(4):
    xbee.receive()

# Listen for wireless status messages from the winches
while True:
    m = xbee.receive() # this does not block
    if m is None: # no new message
        pass
    else:
        # pull out the message from the received data
        cmd = m['payload'].decode('ascii')

        print(cmd)
        
        utime.sleep_ms(100)
