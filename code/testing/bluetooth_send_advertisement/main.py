# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 15:49:34 2022

@author: gavin
"""

from digi import ble
import time

def form_mac_address(addr: bytes) -> str:
    return ":".join('{:02x}'.format(b) for b in addr)

# Form an advertisement payload with a local name
def form_adv_name(header, name):
    payload = bytearray()
    payload.append(len(name) + 1)
    payload.append(header)
    payload.extend(name.encode())
    return payload

# Turn on Bluetooth
ble.active(True)
print("Started Bluetooth with address of: {}".format(form_mac_address(ble.config("mac"))))

payload = form_adv_name(0x08, "Controller 101 status")

# Advertise the new local name with an interval of 100000 microseconds (0.1 seconds).
ble.gap_advertise(100000, payload)

payload = form_adv_name(0xFF, "1,36.4,24,0,0,1000")
for i in range(1000):
    payload = form_adv_name(0xFF, "status: {}".format(i))
    ble.gap_advertise(200000, payload)
    time.sleep(1)
