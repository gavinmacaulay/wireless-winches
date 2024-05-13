from machine import I2C
from fram_i2c import FRAM
from struct import pack, unpack, calcsize
from micropython import const

class storeValue():
    """
    Stores a single value in FRAM with checksum.
    
    Alternates between two storage locations so that if a store fails due
    to power failure during write, the previous storage location can be used
    to get a value.
    
    Memory is used thus:
    byte, usage
    0,    latest pos index
    1,    checksum 
    2-5,  data
    6,    checksum
    7-10, data
    
    """
    
    def __init__(self):
        # Setup access to the FRAM
        self.i2c = I2C(1, freq=400000)
        self.f = FRAM(self.i2c)
        self.posAlternator = self.__storeLocation()
        self.checksum = bytearray(1)
        self.cPos = bytearray(1)
        
        self.storeFormat = const('@f')  # will be used in pack() and unpack()
        self.storeSize = const(calcsize(self.storeFormat))  # bytes 
                    
    def put(self, v):
        """Store the given value."""
        self.cPos[0] = next(self.posAlternator)  # get next location to store at
        ba = bytearray(pack(self.storeFormat, v))  # make bytearray of data
        _ = self.f.readwrite(self.cPos[0]+1, ba, read=False)  # store data
        self.checksum[0] = self.__checksum(ba)
        self.f.readwrite(self.cPos[0], self.checksum, read=False)  # store checksum

        # Store location of most recently written data. If this line succeeds, then
        # all is good. If it fails (e.g. due to loss of power), a read will get the 
        # data in the previous location, which should be good.
        self.f.readwrite(0, self.cPos, read=False)  # store location

    def get(self):
        """Retrieve a value."""
        self.f.readwrite(0, self.cPos, read=True) # get location of most recently written data
        self.f.readwrite(self.cPos[0], self.checksum, read=True) # get checksum
        
        ba = bytearray(self.storeSize)
        _ = self.f.readwrite(self.cPos[0]+1, ba, read=True) # get value

        v, = unpack(self.storeFormat, ba)

        if not (self.checksum[0] == self.__checksum(ba)):
            # should never happen
            raise RuntimeError('Could not read a valid value from FRAM')
        return v
        
    def __checksum(self, ba):
        """XOR checksum of bytearray."""
        csum = 0
        for c in ba:
            csum ^= c
        return csum
        
    def __storeLocation(self):
        """Generator for the two storage locations."""
        while True:
            yield 1
            yield 1+1+self.storeSize
