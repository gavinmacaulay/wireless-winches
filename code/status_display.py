"""Text-based display of winch status.

The only dependency for this code is pyserial.
"""

import serial
import serial.tools.list_ports
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from time import monotonic
import argparse
import signal

@dataclass
class data:
    """Hold data from a winch."""

    voltage: float = 0.0
    temperature: float = 0.0
    position: float = 0.0
    velocity: float = 0.0

def close(signum, frame):
    exit(1)

parser = argparse.ArgumentParser(description='A simple text display of winch status', epilog='Use Ctrl-C to exit')
parser.add_argument('-p', '--port', default=None, help='The serial port to connect to for winch status messages. Will'\
    ' try to automatically use suitable available ports.')

signal.signal(signal.SIGINT, close)

args = parser.parse_args()

# The current version of the controller uses this USB-to-UART chip and it appears
# with this name (under Windows, at least)
serial_port = args.port

if serial_port is None:
    USB_port_name = 'Silicon Labs CP210x USB to UART Bridge'

    while not (comports := list(serial.tools.list_ports.grep(USB_port_name))):
        print('No controller serial port found. Waiting and trying again.')
        sleep(2.0)

    if len(comports) > 1:
        print('More than one suitable serial port was found. Please use the -p option to choose.')
        print('Currently available serial ports are:', ', '.join([p.device for p in comports]))
        exit()

    serial_port = comports[0].device

msg_time = monotonic()
# Pre-allocate to get the keys in the order we want when displaying them
winch_info = {'1': data(), '2': data(), '3': data()}

print(f'Using serial port {serial_port}.')
print('User Ctrl-C to exit')

with serial.Serial(serial_port, 9600, timeout=10) as s:
    s.reset_input_buffer()
    while True:
        line = s.readline().decode('ascii').rstrip()

        try:
            if not line[0].isdigit():
                # not a controller or winch message
                pass
            elif line[0] == '0':
                # the controller status message which we don't deal with
                pass
            else:
                # a winch message
                winch_id, vin, temp, position, velocity, *version = line.split(',')
                winch_info[winch_id] = data(float(vin), float(temp), float(position),
                                            float(velocity))
        except ValueError:
            # print(f'Unable to parse line: "{line}"')
            continue

        if (now := monotonic()) - msg_time > 0.5:  # only update periodically [s]
            msg_time = now
            line1 = 'Line out [m]: '
            line2 = 'Speed [m/s]:  '
            line3 = 'Battery [V]:  '
            line4 = 'Temp [°C]:    '
            for w, d in winch_info.items():
                # ANSI codes here set the colour of the numbers
                line1 += f' \033[32m{d.position:5.2f}\033[0m '
                line2 += f' \033[33m{d.velocity:+5.2f}\033[0m '
                line3 += f'\033[34m{abs(d.voltage):5.1f}\033[0m  '
                line4 += f'\033[36m{abs(d.temperature):5.1f}\033[0m  '

            print()
            # ANSI codes here turn on and off underline
            print('\033[4m      At ' +
                  datetime.today().isoformat(sep=' ', timespec='seconds') +
                  '      \033[0m')
            print('Winch:           1      2      3')
            print(line1)
            print(line2)
            print(line3)
            # ANSI codes here moves the cursor ready for the next display and makes the cursor invisible
            print(line4, end='\033[6A\r\033[?25l')
