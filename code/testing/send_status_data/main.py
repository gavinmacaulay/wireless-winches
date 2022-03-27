# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 17:50:54 2022

@author: gavin
"""

import xbee
from sys import stdin, stdout
import time
from machine import Pin

debug = False

class TicXbee(object):
    def __init__(self):
        # Get the winch id
        self.addr = int(xbee.atcmd('NI')[-1])
    
    def send_command(self, cmd, data_bytes):
        # data_byes should be an iterable data structure
        
        buf = bytearray([cmd])
        if data_bytes:
            buf.extend(bytes(data_bytes))
            
        if debug: print('sending data to tic')
        stdout.buffer.write(buf)
        #relay.send(relay.BLUETOOTH, 'Sent {} bytes to Tic.'.format(len(buf)))
   
    def get_variables(self, offset, length):
        self.send_command(0xA1, [offset, length])
        
        if debug: print('reading from tic')
        result = stdin.buffer.read(length)
        
        if result is None:
            result = []
            
        if debug: print("Expected to read {} bytes, got {}.".format(length, len(result)))
        #relay.send(relay.BLUETOOTH, "Expected to read {} bytes, got {}.".format(length, len(result)))
            
        return bytearray(result) 
   
    def set_current_limit(self, current):
        # A 7-bit write for the current
        current_value = int(current / 40)
        self.send_command(0x91, [current_value & 127])
        
def twos_complement(value, bitWidth):
    #xbee.transmit(xbee.ADDR_BROADCAST, '2s')
    if value >= 2**bitWidth:
        return value # should raise an exception
    else:
        return value - int((value << 1) & 2**bitWidth)
    
led = Pin(Pin.board.D10, Pin.OUT)

tic = TicXbee()

max_payload_len = int(xbee.atcmd('NP'))

xbee.transmit(xbee.ADDR_BROADCAST, 'starting up')

while True:
    xbee.transmit(xbee.ADDR_BROADCAST, 'New loop')
    led.value(True)

    # Get input voltage
    #xbee.transmit(xbee.ADDR_BROADCAST, 'get vin')
    vin_bytes = tic.get_variables(0x33, 2) # [mV], unsigned 16-bit
    vin = int.from_bytes(vin_bytes, 'little', False) / 1000
    
    # Get current limit setting
    #xbee.transmit(xbee.ADDR_BROADCAST, 'get current')
    current_limit_bytes = tic.get_variables(0x4a, 1) # unsigned 8bit, 40 mA steps
    current_limit = int.from_bytes(current_limit_bytes, 'little') * 40
    
    # Get current position
    #xbee.transmit(xbee.ADDR_BROADCAST, 'get position')
    position = tic.get_variables(0x22, 4) # signed 32-bit
    position = int.from_bytes(position, 'little') # microsteps
    #xbee.transmit(xbee.ADDR_BROADCAST, '1')
    position = twos_complement(position, 32)
    #xbee.transmit(xbee.ADDR_BROADCAST, '1')
    
    # Get current velocity
    #xbee.transmit(xbee.ADDR_BROADCAST, 'get velocity')
    velocity = tic.get_variables(0x26, 4) # signed 32-bit
    velocity = int.from_bytes(velocity, 'little') # microsteps per 10000s
    #xbee.transmit(xbee.ADDR_BROADCAST, '2')
    velocity = twos_complement(velocity, 32)
        
    # Get Xbee internal temperature
    xbee_temp = int(xbee.atcmd('TP')) # 2's complement
    if xbee_temp > 0x7FFF:
        xbee_temp = xbee_temp - 0x10000
    
    # Create message and send it to the controller xbee
    data = '{},{:.1f},{},{},{},{}'.format(1, vin, xbee_temp, current_limit, position, velocity)
    if len(data) > max_payload_len:
        data = 'Message too long'
    
    # TODO - change to address of the controller xbee, not broadcast
    if debug: print('Sending ' + data)
    xbee.transmit(xbee.ADDR_BROADCAST, data)
    
    max_velocity = 154607660 * 10000
    if abs(velocity) <= max_velocity * 0.1:
        current_limit = 1000
    elif abs(velocity) <= max_velocity * 0.5:
        current_limit = 1500
    else:
        current_limit = 2820
    
    tic.set_current_limit(current_limit)

    led.value(False)    
    time.sleep(1)


 
