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
        self.f = FRAM(self.i2c, verbose=False)
        self.posAlternator = self.__storeLocation()
        
        self.storeFormat = const('@f')  # will be used in pack() and unpack()
        self.storeSize = const(calcsize(self.storeFormat))  # bytes 
                    
    def put(self, v):
        """Store the given value."""
        self.cPos = next(self.posAlternator)  # get next location to store at
        ba = bytearray(pack(self.storeFormat, v))  # make bytearray of data
        _ = self.f.readwrite(self.cPos+1, ba, read=False)  # store data
        self.f[self.cPos] = self.__checksum(ba)  # store checksum
        # Store location of most recently written data. If this line succeeds, then
        # all is good. If it fails (e.g. due to loss of power), a read will get the 
        # data in the previous location, which should be good.
        self.f[0] = self.cPos  # store location

    def get(self):
        """Retrieve a value."""
        cPos = self.f[0] # get location of most recently written data
        checksum = self.f[cPos]
        ba = bytearray(self.storeSize)
        _ = self.f.readwrite(cPos+1, ba, read=True)
        v, = unpack(self.storeFormat, ba)
        if not (checksum == self.__checksum(ba)):
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
