# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 15:29:09 2022

@author: gavin
"""

from pathlib import Path
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

logDir = Path(os.path.expandvars(r'%PROGRAMDATA%\WirelessWinches\log files'))

logFiles = logDir.glob('*.log')

logFiles = sorted(logFiles)

lastLog = logFiles[-1]

with open(lastLog) as file:
    lines = file.readlines()

w = []
t = []
v = []
p = []
s = []
ts = []
    
for l in lines:
    if 'Received:' in l:
        tt = l.split(',')
        timestamp = tt[0] + '.' + tt[1]
        
        m = re.search("(').+(')", l)
        msg = m[0]
        msg = msg[1:-1]
        parts = msg.split(',')
        if len(parts) == 6:
            (winch_id, vin, xbee_temp, position, velocity, current) = parts
            w.append(winch_id)
            v.append(vin)
            t.append(xbee_temp)
            p.append(position)
            s.append(velocity)
            ts.append(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f'))

df = pd.DataFrame(data={'id': w, 'Vin': v, 'Temperature': t, 'Position': p, 
                        'Velocity': s}, dtype=float)
df['timestamp'] = ts

winches = df['id'].unique()
for w in winches:
    w_df = df[df['id'] == w]
    w_df[['Vin', 'Temperature', 'timestamp']].plot(x='timestamp')
    w_df = w_df.set_index('timestamp')
    
    plt.plot(w_df['Temperature'].rolling('10min').mean(), 'grey')
    plt.plot(w_df['Vin'].rolling('10min').mean(), 'grey')
    plt.title(f'Winch {w:.0f}')
    plt.grid()

