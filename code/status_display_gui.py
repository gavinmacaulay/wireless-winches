# -*- coding: utf-8 -*-
"""
Displays winch status

@author: gavinj
"""

import queue
import numpy as np

import threading
import logging, logging.handlers
from datetime import datetime, timedelta
import os, sys
from tkinter import font
import tkinter as tk
import tkinter.ttk as ttk
from time import sleep
from collections import namedtuple
import serial
import serial.tools.list_ports
from pathlib import Path

if sys.platform == "win32":
    import win32api

# queue to communicate between two threads
queue = queue.Queue()
root = tk.Tk()
global job # handle to the function that does the echogram drawing

def main():
    # Directory where log files go. Windows specific
    logdir = os.path.expandvars(r'%PROGRAMDATA%\WirelessWinches\log files')
    # make the directory
    Path(logdir).mkdir(parents=True, exist_ok=True) 
    setupLogging(logdir, 'Winches')
    
    # Serial port to listen to.
    xbeeCOMport = 'COM6'

    # logging.info('Finding COM ports.')
    # comports = serial.tools.list_ports.comports()
    # comports = sorted(comports, key=lambda port: int(port.device[3:])) # sort on com port number
    
    # logging.info('Available COM ports are:')
    # for p in comports:   
    #     logging.info('Name: {port.device}, Description: {port.description}'.format(port=p))
    
    # [selectedCOMports[0]] = [p.device for p in comports if 'Silicon Labs CP210x USB to UART Bridge' in p.description] or [selectedCOMports[0]]
    
    logging.info('Selected COM port: {}'.format(xbeeCOMport))

    # Does the parsing and display of winch stats
    display = dataDisplayer()

    # The GUI window
    root.title('Wireless winch status ({})'.format(xbeeCOMport))
    
    # Up the default font size
    default_font = font.nametofont('TkDefaultFont')
    default_font.configure(size=24)

    # A line for the time
    timestampLabel = ttk.Label(root, text='Time unknown...')
    timestampLabel.grid(row=0, column=0, columnspan=4)

    ttk.Label(root, text='Winch [m]:').grid(row=1, sticky=tk.E)
    for i in range(3):
        w_label = ttk.Label(root, text=f'{i+1}', anchor='e', width=10)
        w_label.grid(row=1, column=i+1, padx=5, sticky=tk.E+tk.W)

    ttk.Label(root, text='Line out [m]:').grid(row=2, sticky=tk.E)
    wire_out = []
    for i in range(3):
        wire_out.append(ttk.Label(root, text='--', anchor='e', width=10))
        wire_out[i].grid(row=2, column=i+1, padx=5, sticky=tk.E+tk.W)

    ttk.Label(root, text='Speed [m/s]:').grid(row=3, sticky=tk.E)
    velocity = []
    for i in range(3):
        velocity.append(ttk.Label(root, text='--', anchor='e'))
        velocity[i].grid(row=3, column=i+1, padx=5, sticky=tk.E+tk.W)

    ttk.Label(root, text='Temperature [°C]:').grid(row=4, sticky=tk.E)
    temp = []
    for i in range(3):
        temp.append(ttk.Label(root, text='--', anchor='e'))
        temp[i].grid(row=4, column=i+1, padx=5, sticky=tk.E+tk.W)

    ttk.Label(root, text='Battery [V]:').grid(row=5, sticky=tk.E)
    batt = []
    for i in range(3):
        batt.append(ttk.Label(root, text='--', anchor='e'))
        batt[i].grid(row=5, column=i+1, padx=5, sticky=tk.E+tk.W)

    Widgets = namedtuple('widgets', 'time, p, v, t, b')
    widgets = Widgets(time=timestampLabel, p=wire_out, v=velocity,
                      t=temp, b=batt)
    
    # Config, and Close buttons
    ttk.Separator(root).grid(row=6, columnspan=4, sticky=tk.EW)
    frame = tk.Frame()
    frame.grid(row=7, column=0, columnspan=4, sticky=tk.NSEW)
    
    ttk.Button(frame, text='Config', command=display.openConfigDialog).grid(row=0, column=0, sticky=tk.NSEW)
    ttk.Button(frame, text='Close', command=window_closed).grid(row=0, column=1, sticky=tk.NSEW)

    for i in range(0, frame.grid_size()[0]):
       frame.grid_columnconfigure(i, weight=1)

    # Make the widgets in the grid expand to fill the space available
    for i in range(0, root.grid_size()[0]):
        root.grid_columnconfigure(i, weight=1)
    for i in range(0, root.grid_size()[1]):
        root.grid_rowconfigure(i, weight=0)

    # Create the threads that listen for messages from the hand controller
    t1 = threading.Thread(target=COM_listen, args=(xbeeCOMport, 'object',))
    t1.daemon = True # makes the thread close when main() ends
    
    # Start the thread
    t1.start()

    # For Windows, catch when the console is closed
    if sys.platform == "win32":
        win32api.SetConsoleCtrlHandler(on_exit, True)

    # Check periodically for new data
    global job
    job = root.after(display.checkQueueInterval, display.newData, root, widgets)
    
    # And start things...
    root.protocol("WM_DELETE_WINDOW", window_closed)
    root.mainloop()
        
def on_exit(sig, func=None):
    "Called when the Windows cmd console closes"
    window_closed()
    
def window_closed():
    "Called to nicely end the whole program"
    global job
    root.after_cancel(job)
    logging.info('Program ending...')
    root.quit()
    
def COM_listen(port, dataSource):
    " Listen for new data on the com port and put them onto a queue"

    Data = namedtuple('data', 'timestamp, source, reading')

    while True:
        try:
            f = serial.Serial(port, baudrate=9600, timeout=10)
            f.reset_input_buffer()
        except:
            logging.error(sys.exc_info()[1])
            sleep(2.0)
        else:
            try:
                logging.info('Listening to port: {}.'.format(port))
            
                while True:
                    line = f.readline()

                    try:
                        line = line.decode('utf-8')
                    except UnicodeDecodeError:
                        pass
                    else:
                        t = datetime.utcnow()
                        data = Data(timestamp=t, source=dataSource, reading=line)
                        queue.put(data)
            except:
                logging.warning(sys.exc_info()[1])
                f.close()
            
            sleep(2.0)
            logging.info("Trying to re-open port '{}'".format(port))

class dataDisplayer:
    "Receive via queues messages from the balances and update the data display"
    
    def __init__(self):    
        
        self.checkQueueInterval = 100 # [ms] duration between checking the queue of received
        
        self.position = np.array([np.nan, np.nan, np.nan])
        self.velocity = np.array([np.nan, np.nan, np.nan])
        self.temperature = np.array([np.nan, np.nan, np.nan])
        self.battery = np.array([np.nan, np.nan, np.nan])
        
    def updateUI(self, timestamp, widgets):

        widgets.time.config(text='{:%Y-%m-%d (%a) %H:%M:%S UTC}'.format(timestamp))
        
        for i in range(3):
            widgets.p[i].config(text='{:.2f}'.format(self.position[i]))
            widgets.v[i].config(text='{:.2f}{}'.format(abs(self.velocity[i]), self.getDirectionArrow(self.velocity[i])))
            widgets.t[i].config(text='{:.0f}'.format(self.temperature[i]))
            widgets.b[i].config(text='{}'.format(self.battery[i]))         

    def getDirectionArrow(self, v):
        dirn = ''
        if v < 0:
            dirn = '\u2191'
        elif v > 0:
            dirn = '\u2193'
        return dirn
        
    def newData(self, root, widgets):
        "Receives messages from the queue, decodes them, and updates the display"
     
        while not queue.empty():
            message = queue.get(block=False)
            try:
                logging.debug("Received: '{}'".format(message))

                if len(message.reading): # CR LF is already chopped off
                
                    line = message.reading
                    line = line.rstrip()      
                
                    parts = line.split(',')
                    if len(parts) == 6:
                        (winch_id, vin, xbee_temp, position, velocity, current) = parts
                        velocity = to_float(velocity)
                        position = to_float(position)
                    
                        i = int(winch_id) - 1
                        self.position[i] = position
                        self.velocity[i] = velocity
                        self.temperature[i] = xbee_temp
                        self.battery[i] = vin

                        # for testing                    
                        self.position[i+1] = position
                        self.velocity[i+1] = velocity
                        self.temperature[i+1] = xbee_temp
                        self.battery[i+1] = vin

                        self.position[i+2] = position
                        self.velocity[i+2] = velocity
                        self.temperature[i+2] = xbee_temp
                        self.battery[i+2] = vin

                        self.updateUI(message.timestamp, widgets)
                    else:
                        logging.warning('Received malformed data: ' + line)

            except None:  # if anything goes wrong in the parsing, just ignore it...
                e = sys.exc_info()
                logging.warning('Error when parsing balance message. Waiting for next message.')
                logging.warning(e)  
                pass

        global job
        job = root.after(self.checkQueueInterval, self.newData, root, widgets)
        
    def openConfigDialog(self):
        inputDialog = configDialog(root)
        root.wait_window(inputDialog.top)
        print('Reference weight mass [g]: ', inputDialog.referenceMass)
        # does inputDialog get cleaned up here?

            
class configDialog:
    def __init__(self, parent):
        # self.refCOMport = tk.StringVar()
        # self.krillCOMport = tk.StringVar()
        # COMports = ('COM3', 'COM4', 'COM5')

        # top = self.top = tk.Toplevel(parent)
        # self.refMassLabel = tk.Label(top, text='Reference mass [g]')
        # self.refMassEntry = tk.Entry(top)
        # self.refMassLabel.grid(row=0)
        # self.refMassEntry.grid(row=0,column=1)
        
        # self.refBalanceLabel = tk.Label(top, text='Reference balance COM port')
        # self.krillBalanceLabel = tk.Label(top, text='Krill balance COM port')
        # self.refBalanceList = ttk.Combobox(top, textvariable=self.refCOMport)
        # self.refBalanceList['values'] = COMports
        # self.krillBalanceList = ttk.Combobox(top, textvariable=self.krillCOMport)
        # self.krillBalanceList['values'] = COMports

        # self.refBalanceLabel.grid(row=1)
        # self.refBalanceList.grid(row=1,column=1)
        # self.krillBalanceLabel.grid(row=2)
        # self.krillBalanceList.grid(row=2,column=1)
        
        self.OKButton = ttk.Button(top, text='OK', command=self.send)
        self.OKButton.grid(row=3,column=0)
        
        self.cancelButton = ttk.Button(top, text='Cancel', command=self.close)
        self.cancelButton.grid(row=3,column=1)

    def send(self):
        # self.referenceMass = self.refMassEntry.get()
        # self.refBalancePort = ''
        # self.krillBalancePort = ''
        self.close()
        
    def close(self):
        self.top.destroy()
        
def to_float(x):
    try:
        return float(x)
    except ValueError:
        return float('NaN')

def setupLogging(log_dir, label):

    # Setup info, warning, and error message logger to a file and to the console
    now = datetime.utcnow()
    logger_filename = os.path.join(log_dir, now.strftime('log_' + label + '-%Y%m%d-T%H%M%S.log'))
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s')

    # A logger to a file that is changed periodically
    rotatingFile = logging.handlers.TimedRotatingFileHandler(logger_filename, when='H', interval=12, utc=True)
    rotatingFile.setFormatter(formatter)
    logger.addHandler(rotatingFile)

    # add a second output to the logger to direct messages to the console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    logging.info('Log files are in ' + log_dir)
      
if __name__== "__main__":
    main()

