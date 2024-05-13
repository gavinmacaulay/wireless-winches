# fram_i2c.py Driver for Fujitsu 16K Ferroelectric RAM module (Fujitsu MB85RC16)

from micropython import const

_SIZE = const(2048)  # Chip size [bytes]
_ADDR = const(0x50)  # FRAM I2C address 0x50 to 0x57

class FRAM():
    def __init__(self, i2c):
        self._i2c = i2c
        self.lsb = bytearray(1)
        self.i2c_addr = bytearray(1)

    def scan(self, verbose=False):
        devices = self._i2c.scan()
        chips = [d for d in devices if d == _ADDR]
        if len(chips) == 0:
            raise RuntimeError("FRAM not found at hard-wired address.")
        if verbose:
            print("Chip detected at hard-wired MB85RC16 address")
        return chips

    def readwrite(self, loc, buf, read):
        mvb = memoryview(buf)
        if len(buf) > 0:
            msb = (loc << 5) >> 13 # top 3 bits of lowest 11 bits
            self.lsb[0] = loc & 0xFF # lowest 8 bits of 11 bits
            self.i2c_addr[0] = _ADDR + msb # I2C address (7 bits)

            if read:
                self._i2c.writeto(self.i2c_addr[0], self.lsb)
                self._i2c.readfrom_into(self.i2c_addr[0], mvb)
            else: # write
                self._i2c.writevto(self.i2c_addr[0], (self.lsb, mvb))
        return buf
