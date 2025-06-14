"""Displays winch status.

The dependencies for this code are numpy and pyserial.
"""

import queue
import numpy as np

import threading
import logging
import logging.handlers
from datetime import datetime as dt
import os
import sys
from tkinter import font
import tkinter as tk
import tkinter.ttk as ttk
from time import sleep
from collections import namedtuple
import serial
import serial.tools.list_ports
from pathlib import Path
import time

if sys.platform == "win32":
    import win32api

# queue to communicate between two threads
queue = queue.Queue()
root = tk.Tk()
global job  # handle to the function that does the echogram drawing


def main():
    """Create and run the GUI."""
    # Directory where log files go. Windows specific
    logdir = os.path.expandvars(r'%PROGRAMDATA%\WirelessWinches\log files')
    # make the directory
    Path(logdir).mkdir(parents=True, exist_ok=True)
    setupLogging(logdir, 'Winches')

    # Serial port to listen to.
    # xbeeCOMport = 'COM8'

    xbeeUSBPortName = 'Silicon Labs CP210x USB to UART Bridge'
    while not (comports := list(serial.tools.list_ports.grep(xbeeUSBPortName))):
        logging.info('No controller serial port found. Trying again.')
        sleep(2.0)
    xbeeCOMport = comports[0].device

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

    ttk.Label(root, text='Winch:').grid(row=1, sticky=tk.E)
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

    # Controller information
    ttk.Separator(root).grid(row=6, columnspan=4, sticky=tk.EW)
    controller_status = ttk.Label(root, text='', font=('TkDefaultFont', 12))
    controller_status.grid(row=7, columnspan=4, sticky=tk.EW)

    # Config, and Close buttons
    frame = tk.Frame()
    frame.grid(row=8, column=0, columnspan=4, sticky=tk.NSEW)

    ttk.Button(frame, text='Config', command=display.openConfigDialog).grid(row=0, column=0,
                                                                            sticky=tk.NSEW)
    ttk.Button(frame, text='Close', command=window_closed).grid(row=0, column=1, sticky=tk.NSEW)

    for i in range(0, frame.grid_size()[0]):
        frame.grid_columnconfigure(i, weight=1)

    # Make the widgets in the grid expand to fill the space available
    for i in range(0, root.grid_size()[0]):
        root.grid_columnconfigure(i, weight=1)
    for i in range(0, root.grid_size()[1]):
        root.grid_rowconfigure(i, weight=0)

    Widgets = namedtuple('widgets', 'time, p, v, t, b, c')
    widgets = Widgets(time=timestampLabel, p=wire_out, v=velocity,
                      t=temp, b=batt, c=controller_status)

    # Create the threads that listen for messages from the hand controller
    t1 = threading.Thread(target=COM_listen, args=(xbeeCOMport, 'object',))
    t1.daemon = True  # makes the thread close when main() ends

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
    """Is called when the Windows cmd console closes."""
    window_closed()


def window_closed():
    """Is called to nicely end the whole program."""
    global job
    root.after_cancel(job)
    logging.info('Program ending...')
    root.quit()


def COM_listen(port, dataSource):
    """Listen for new data on the com port and put them onto a queue."""
    Data = namedtuple('data', 'timestamp, source, reading')

    while True:
        try:
            f = serial.Serial(port, baudrate=9600, timeout=10)
            f.reset_input_buffer()
        except (ValueError, serial.SerialException):
            logging.error(sys.exc_info()[1])
            queue.put(Data(timestamp=dt.utcnow(), source=dataSource, reading='no com port'))
            sleep(2.0)
        else:
            try:
                logging.info('Listening to serial port {}.'.format(port))

                while True:
                    line = f.readline()

                    if not line:  # probably timed out
                        queue.put(Data(timestamp=dt.now(), source=dataSource,
                                       reading='timed out'))
                    else:
                        try:
                            line = line.decode('utf-8')
                        except UnicodeDecodeError:
                            pass
                        else:
                            t = dt.utcnow()
                            data = Data(timestamp=t, source=dataSource, reading=line)
                            queue.put(data)
            except Exception:
                logging.warning(sys.exc_info()[1])
                f.close()

            sleep(2.0)
            logging.info("Trying to re-open port '{}'".format(port))


class dataDisplayer:
    """Receive via queue messages and update the data display."""

    def __init__(self):

        self.checkQueueInterval = 100  # [ms] duration between checking the queue of received

        self.rawPosition = np.array([np.nan, np.nan, np.nan])
        self.lastRawPosition = np.array([np.nan, np.nan, np.nan])

        self.position = np.array([np.nan, np.nan, np.nan])
        self.velocity = np.array([np.nan, np.nan, np.nan])
        self.temperature = np.array([np.nan, np.nan, np.nan])
        self.temperatureRaw = np.full((3, 100), np.nan)
        self.battery = np.array([np.nan, np.nan, np.nan])
        self.batteryRaw = np.full((3, 100), np.nan)
        self.dataReceivedTime = [time.time(), time.time(), time.time()]

        self.positionOffset = np.array([0.0, 0.0, 0.0])

        self.style = ttk.Style()
        self.style.configure("LowBattVoltage.TLabel", foreground="red")
        self.style.configure("NormalBattVoltage.TLabel", foreground="black")
        self.newTimeout = [True, True, True]

        self.LowBattVoltageLevel = 33.0  # [V]
        self.noDataTimeout = 1.5  # [s] UI goes grey if no messages in this time
        self.maxPositionJump = 1  # [m] larger than this is taken as loss of power at winch

        self.controller_voltage = np.nan
        self.controller_id = None
        self.controller_soc = np.nan

    def updateUI(self, timestamp, widgets):
        """Update the GUI."""
        widgets.time.config(text='{:%Y-%m-%d %H:%M:%S UTC}'.format(timestamp))

        now = time.time()

        for i in range(3):
            if (now - self.dataReceivedTime[i]) > self.noDataTimeout:
                state = 'disabled'
                if self.newTimeout[i]:
                    logging.info('Message timeout on winch ' + str(i+1))
                    self.newTimeout[i] = False
            else:
                state = 'enabled'
                if not self.newTimeout[i]:
                    logging.info('Messages received again from winch ' + str(i+1))
                    self.newTimeout[i] = True

            widgets.p[i].config(text='{:.2f}'.format(self.position[i]), state=state)
            widgets.v[i].config(text='{:.2f}{}'.format(abs(self.velocity[i]),
                                self.getDirectionArrow(self.velocity[i])), state=state)
            widgets.t[i].config(text='{:.1f}'.format(self.temperature[i]), state=state)

            battStyle = "NormalBattVoltage.TLabel"
            if self.battery[i] < self.LowBattVoltageLevel:
                battStyle = "LowBattVoltage.TLabel"

            widgets.b[i].config(text='{:.1f}'.format(self.battery[i]), style=battStyle, state=state)

        print(self.controller_id)
        if self.controller_id:
            widgets.c.config(text=f'Controller {self.controller_id} '
                             f'({self.controller_soc:.0f}% battery)')

    def getDirectionArrow(self, v):
        """Return an appropriate arrow character."""
        dirn = ''
        if v < 0:
            dirn = '\u2191'
        elif v > 0:
            dirn = '\u2193'
        return dirn

    def newData(self, root, widgets):
        """Receives messages from the queue, decodes them, and updates the display."""
        while not queue.empty():
            message = queue.get(block=False)
            try:
                logging.debug("Received: '{}'".format(message))

                if len(message.reading):  # CR LF is already chopped off

                    line = message.reading
                    line = line.rstrip()
                    logging.debug("Received: '{}'".format(line))
                    parts = line.split(',')

                    if parts[0] >= '1' and len(parts) >= 5:
                        (winch_id, vin, xbee_temp, position, velocity) = parts
                        velocity = to_float(velocity)
                        position = to_float(position)

                        i = int(winch_id) - 1
                        self.lastRawPosition[i] = self.rawPosition[i]
                        self.rawPosition[i] = position

                        # Detect a power reset on a winch and adjust offset to keep
                        # the position the same as before the power reset. This assumes
                        # that the winch was not rotated when powered off.
                        if abs(self.rawPosition[i] - self.lastRawPosition[i])\
                                > self.maxPositionJump:
                            logging.info('Jump in winch position - power restored to winch ' +
                                         str(i + 1) + '?')
                            self.positionOffset[i] +=\
                                (self.lastRawPosition[i] - self.rawPosition[i])

                        self.position[i] = self.rawPosition[i] + self.positionOffset[i]

                        self.velocity[i] = velocity

                        self.temperatureRaw[i, 0:-1] = self.temperatureRaw[i, 1:]  # shift
                        self.temperatureRaw[i, -1] = xbee_temp
                        self.temperature[i] = np.nanmean(self.temperatureRaw[i, :])

                        self.batteryRaw[i, 0:-1] = self.batteryRaw[i, 1:]  # shift
                        self.batteryRaw[i, -1] = vin
                        self.battery[i] = np.nanmean(self.batteryRaw[i, :])

                        self.dataReceivedTime[i] = time.time()

                        self.updateUI(message.timestamp, widgets)
                    elif line[0] == '0':
                        if len(parts) == 6:
                            (_, controller_id, mode, voltage, soc, rate) = parts
                            self.controller_voltage = to_float(voltage)
                            self.controller_id = controller_id
                            self.controller_soc = to_float(soc)
                    elif (line == 'no com port') or (line == 'timed out'):
                        # force the UI to go grey
                        for i in range(3):
                            self.dataReceivedTime[i] = time.time() - 2*self.noDataTimeout
                            self.updateUI(message.timestamp, widgets)
                    else:
                        logging.warning('Received malformed data: ' + line)

            except Exception:  # if anything goes wrong in the parsing, just ignore it...
                e = sys.exc_info()
                logging.warning('Error when parsing balance message. Waiting for next message.')
                logging.warning(e)

        global job
        job = root.after(self.checkQueueInterval, self.newData, root, widgets)

    def openConfigDialog(self):
        """Open the config dialog."""
        inputDialog = configDialog(root, self.positionOffset)
        root.wait_window(inputDialog.top)
        for i in range(3):
            self.positionOffset[i] = inputDialog.zeroValue[i].get()


class configDialog:
    """Implement the config dialog."""

    def __init__(self, parent, offsets):

        default_font = font.nametofont('TkDefaultFont')
        default_font.configure(size=24)

        self.zeroValue = [tk.StringVar(root, value=str(offsets[0])),
                          tk.StringVar(root, value=str(offsets[1])),
                          tk.StringVar(root, value=str(offsets[2]))]

        self.top = tk.Toplevel(parent)
        for i in range(3):
            ttk.Label(self.top, text='Winch {} offset [m]:'.format(i+1)).grid(row=i+1, column=0)
            ttk.Entry(self.top, font=default_font, justify=tk.CENTER,
                      textvariable=self.zeroValue[i]).grid(row=i+1, column=1)

        ttk.Separator(self.top).grid(row=4, columnspan=2, sticky=tk.EW)
        frame = tk.Frame(self.top)
        frame.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW)

        self.OKButton = ttk.Button(frame, text='Close', command=self.close).grid(row=0, column=0,
                                                                                 sticky=tk.NSEW)

        for i in range(0, frame.grid_size()[0]):
            frame.grid_columnconfigure(i, weight=1)

        # Make the widgets in the grid expand to fill the space available
        for i in range(0, self.top.grid_size()[0]):
            self.top.grid_columnconfigure(i, weight=1)
        for i in range(0, self.top.grid_size()[1]):
            self.top.grid_rowconfigure(i, weight=0)

    def close(self):  # noqa
        self.top.destroy()


def to_float(x):  # noqa
    try:
        return float(x)
    except ValueError:
        return float('NaN')


def setupLogging(log_dir, label):
    """Configure info, warning, and error message logger to a file and to the console."""
    now = dt.utcnow()
    logger_filename = os.path.join(log_dir, now.strftime('log_' + label + '-%Y%m%d-T%H%M%S.log'))
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s')

    # A logger to a file that is changed periodically
    rotatingFile = logging.handlers.TimedRotatingFileHandler(logger_filename, when='H',
                                                             interval=12, utc=True)
    rotatingFile.setFormatter(formatter)
    logger.addHandler(rotatingFile)

    # add a second output to the logger to direct messages to the console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    logging.info('Log files are in ' + log_dir)


if __name__ == "__main__":
    main()
