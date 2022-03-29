# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 17:24:15 2022

@author: gavin
"""
import serial
from datetime import datetime

# A simple display of winch status

# Receive data from USB/serial port

with serial.Serial('COM6', 9600, timeout=10) as s:
    s.reset_input_buffer()
    while True:
        line = s.readline()
        print(line)
        line = line.decode('ascii').rstrip()

        try:       
            winch_id, vin, xbee_temp, position, velocity, current = line.split(',')
        except ValueError:
            print(f'Unable to parse line: "{line}"')
            continue
        
        velocity = float(velocity)
        position = float(position)
        
        speed = abs(velocity)
        if velocity > 0:
            direction = 'out'
        elif velocity < 0:
            direction = 'in'
        else:
            direction = ''

        now = datetime.today().isoformat()
        
        print(now)
        print(f'Winch {winch_id}: Vin = {vin} V, XBee temperature = {xbee_temp} °C')
        print(f'        Line out = {position:.2f} m, Speed = {speed:.2f} m/s {direction}')
        print(f'        Max current setting = {current} mA')
        
# Make a scrolling text display

# Make a UI that shows the winch status

