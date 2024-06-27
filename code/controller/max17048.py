"""Max17043 library for MicroPython.

this is a lipo battery cells fuel gauge made by maxim
https://datasheets.maximintegrated.com/en/ds/MAX17043-MAX17044.pdf
small module by sparkfun
https://www.sparkfun.com/products/10617
based upon the max17043 library for arduino by lucadentella
https://github.com/lucadentella/ArduinoLib_MAX17043

Andre Peeters
2017/10/31
"""

from machine import I2C
import binascii
import struct


class max17048:
    """Class to communicate with a MAX17408 battery fuel guage."""

    REGISTER_VCELL = 0X02
    REGISTER_SOC = 0X04
    REGISTER_MODE = 0X06
    REGISTER_VERSION = 0X08
    REGISTER_ID = 0x19
    REGISTER_CONFIG = 0X0C
    REGISTER_COMMAND = 0XFE
    REGISTER_CRATE = 0x16

    def __init__(self):
        self.i2c = I2C(1, freq=400000)
        self.max17048Address = (self.i2c.scan())[0]

    def __str__(self):
        """Get string representation of the values."""
        rs = "i2c address is {}\n".format(self.max17048Address)
        rs += "version is {}\n".format(self.getVersion())
        rs += "id is {}\n".format(self.getID())
        rs += "Battery voltage is {:.2f} V\n".format(self.getVCell())
        rs += "Charge rate is {:.2f} %/hr\n".format(self.getChargeRate())
        rs += "SOC is {:.1f} %\n".format(self.getSOC())
        rs += "alert threshold is {}%\n".format(self.getAlertThreshold())
        rs += "in alert is {}".format(self.inAlert())
        return rs

    def address(self):
        """Return the i2c address."""
        return self.max17048Address

    def reset(self):
        """Reset."""
        self.__writeRegister(self.REGISTER_COMMAND, binascii.unhexlify('0054'))

    def getVCell(self):
        """Get the volts left in the cell."""
        buf = self.__readRegister(self.REGISTER_VCELL)
        v = struct.unpack_from(">H", buf, 0)[0]
        return v * 78.125 / 1_000_000

    def getSOC(self):
        """Get the state of charge."""
        buf = self.__readRegister(self.REGISTER_SOC)
        v = struct.unpack_from(">H", buf, 0)[0]
        return v / 256.0

    def getChargeRate(self):
        """Get the charge or discharge rate [%/hr]."""
        buf = self.__readRegister(self.REGISTER_CRATE)
        v = struct.unpack_from(">h", buf, 0)[0]
        return v * 0.208

    def getVersion(self):
        """Get the version of the max17048 module."""
        buf = self.__readRegister(self.REGISTER_VERSION)
        return struct.unpack(">H", buf)[0]

    def getID(self):
        """Get ID."""
        buf = self.__readRegister(self.REGISTER_ID)
        return struct.unpack(">B", buf)[0]

    def getAlertThreshold(self):
        """Get the alert level."""
        return (32 - (self.__readConfigRegister()[1] & 0x1f))

    def hibernating(self):
        """Get hibernating state."""
        d = self.__readRegister(self.REGISTER_MODE)[0] & 0b00010000
        return d > 0

    def setAlertThreshold(self, threshold):
        """Set the alert level."""
        self.threshold = 32 - threshold if threshold < 32 else 32
        buf = self.__readConfigRegister()
        buf[1] = (buf[1] & 0xE0) | self.threshold
        self.__writeConfigRegister(buf)

    def inAlert(self):
        """Check if the the max17048 module is in alert."""
        return (self.__readConfigRegister())[1] & 0x20

    def clearAlert(self):
        """Clear the alert."""
        self.__readConfigRegister()

    def quickStart(self):
        """Do a quick restart."""
        self.__writeRegister(self.REGISTER_MODE, binascii.unhexlify('4000'))

    def __readRegister(self, address):
        """Read the register at address, always returns bytearray of 2 char."""
        return self.i2c.readfrom_mem(self.max17048Address, address, 2)

    def __readConfigRegister(self):
        """Read the config register, always returns bytearray of 2 char."""
        return self.__readRegister(self.REGISTER_CONFIG)

    def __writeRegister(self, address, buf):
        """Write buf to the register address."""
        self.i2c.writeto_mem(self.max17048Address, address, buf)

    def __writeConfigRegister(self, buf):
        """Write buf to the config register."""
        self.__writeRegister(self.REGISTER_CONFIG, buf)
