# bdevice.py Hardware-agnostic base classes.
# BlockDevice Base class for general block devices e.g. EEPROM, FRAM.
# FlashDevice Base class for generic Flash memory (subclass of BlockDevice).
# Documentation in BASE_CLASSES.md

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2024 Peter Hinch

from micropython import const


class BlockDevice:
    def __init__(self, nbits, nchips, chip_size):
        self._c_bytes = chip_size  # Size of chip in bytes
        self._a_bytes = chip_size * nchips  # Size of array
        self._nbits = nbits  # Block size in bits
        self._block_size = 2 ** nbits
        self._rwbuf = bytearray(1)

    def __len__(self):
        return self._a_bytes

    def __setitem__(self, addr, value):
        if isinstance(addr, slice):
            return self._wslice(addr, value)
        self._rwbuf[0] = value
        self.readwrite(addr, self._rwbuf, False)

    def __getitem__(self, addr):
        if isinstance(addr, slice):
            return self._rslice(addr)
        return self.readwrite(addr, self._rwbuf, True)[0]

    # Handle special cases of a slice. Always return a pair of positive indices.
    def _do_slice(self, addr):
        if not (addr.step is None or addr.step == 1):
            raise NotImplementedError("only slices with step=1 (aka None) are supported")
        start = addr.start if addr.start is not None else 0
        stop = addr.stop if addr.stop is not None else self._a_bytes
        start = start if start >= 0 else self._a_bytes + start
        stop = stop if stop >= 0 else self._a_bytes + stop
        return start, stop

    def _wslice(self, addr, value):
        start, stop = self._do_slice(addr)
        try:
            if len(value) == (stop - start):
                res = self.readwrite(start, value, False)
            else:
                raise RuntimeError("Slice must have same length as data")
        except TypeError:
            raise RuntimeError("Can only assign bytes/bytearray to a slice")
        return res

    def _rslice(self, addr):
        start, stop = self._do_slice(addr)
        buf = bytearray(stop - start)
        return self.readwrite(start, buf, True)

    # IOCTL protocol.
    def sync(self):  # Nothing to do for unbuffered devices. Subclass overrides.
        return

    def readblocks(self, blocknum, buf, offset=0):
        self.readwrite(offset + (blocknum << self._nbits), buf, True)

    def writeblocks(self, blocknum, buf, offset=0):
        self.readwrite(offset + (blocknum << self._nbits), buf, False)

    # https://docs.micropython.org/en/latest/library/os.html#os.AbstractBlockDev.ioctl
    def ioctl(self, op, arg):  # ioctl calls: see extmod/vfs.h
        if op == 3:  # SYNCHRONISE
            self.sync()
            return
        if op == 4:  # BP_IOCTL_SEC_COUNT
            return self._a_bytes >> self._nbits
        if op == 5:  # BP_IOCTL_SEC_SIZE
            return self._block_size
        if op == 6:  # Ignore ERASE because handled by driver.
            return 0
