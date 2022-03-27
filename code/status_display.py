# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 17:24:15 2022

@author: gavin
"""
import serial

# A simple display of winch status

# Receive data from USB/serial port

with serial.Serial('COM6', 9600, timeout=10) as s:
    s.reset_input_buffer()
    while True:
        line = s.readline()
        
        line = line.decode('ascii').rstrip()
        
        winch_id, vin, xbee_temp, current, position, velocity = line.split(',')
        
        velocity = int(velocity)
        position = int(position)
        
        speed = abs(velocity)
        if velocity < 0:
            direction = 'down'
        elif velocity > 0:
            direction = 'up'
        else:
            direction = ''
        
        speed = speed / 1e6 / 25
        position = position / 1e6
        
        print(f'Winch {winch_id}: Vin = {vin} V, XBee temperature = {xbee_temp} °C')
        print(f'        Line out = {position:.2f} m, Speed = {speed:.2f} m/s {direction}')
        print(f'        Max current setting = {current} mA')
        
# Make a scrolling text display

# Make a UI that shows the winch status

