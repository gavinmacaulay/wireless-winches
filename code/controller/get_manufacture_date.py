# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:51:40 2023

@author: gavin
"""
#import math
import xbee

def civil_from_days(z):
    """
    Date from days since 1-1-1900
    """
    z += 719469 - 25567 # shift to date 0000-03-01
    #era = int(math.floor((z if z >= 0 else z - 146096) / 146097))
    #doe = int(math.floor(z - era * 146097))          # [0, 146096]
    era = int((z if z >= 0 else z - 146096) / 146097)
    doe = int(z - era * 146097)          # [0, 146096]

    yoe = int((doe - doe/1460 + doe/36524 - doe/146096) / 365)  # [0, 399]
    y = int(yoe) + era * 400
    doy = int(doe - (365*yoe + yoe/4 - yoe/100))                # [0, 365]
    mp = int((5*doy + 2)/153)                                   # [0, 11]
    d = int(doy - (153*mp+2)/5 + 1)                             # [1, 31]
    m = mp+3 if mp < 10 else mp-9                              # [1, 12]
    
    return y + (m <= 2), m, d

def get_manufacture_date():
    dd = xbee.atcmd('D%')
    days_since = int.from_bytes(dd[0:3], 'big')
    hour_of_day = dd[3]
    
    date = civil_from_days(days_since)
    
    return 'Manufacture occured on {}-{}-{} at {:02d}:00.'.format(date[0], date[1], date[2]


