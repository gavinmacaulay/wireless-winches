# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 13:21:08 2022

@author: gavin
"""

import machine
import utime
import xbee
import sys
from xbee import relay

v = [39.0, 40.0, 41.0]
t = [21.0, 22.0, 23.0]
l = [0.0, 0.0, 0.0]
s = [0.0, 0.0, 0.0]

voltage_limits = [30.0, 45.0]
temp_limits = [20.0, 70.0]
line_limits = [-30.0, 90.0]
speed_limits = [-1.0, 1.0]

voltage_step = 0.01
temp_step = 0.1
line_step = 0.01
speed_step = 0.01

while True:
    try:
        for winch in range(3):
            # winch_id,voltage,line_out,line_speed,temperature
            v[winch] = v[winch] + voltage_step
            if v[winch] > voltage_limits[1]:
                v[winch] = voltage_limits[0]
                
            t[winch] = t[winch] + temp_step
            if t[winch] > temp_limits[1]:
                t[winch] = temp_limits[0]
                
            l[winch] = l[winch] + line_step
            if l[winch] > line_limits[1]:
                l[winch] = line_limits[0]
                
            s[winch] = s[winch] + speed_step
            if s[winch] > speed_limits[1]:
                s[winch] = speed_limits[0]
                
            status = '{},{:.1f},{:.0f},{:.1f},{:.2f}'.format(winch+1, v[winch], t[winch], l[winch], s[winch])
            print(status)
        
            try:
                print('Send relay message')
                relay.send(relay.BLUETOOTH, status)
            except Exception as e:
                print('Exception during relay.send: ' + str(e))
            
            utime.sleep_ms(250)
                        
    except Exception as e:
        print('Exception caught: ', str(e))

    utime.sleep_ms(1000)
