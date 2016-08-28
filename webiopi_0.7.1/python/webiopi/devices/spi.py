#   Copyright 2012-2013 Eric Ptak - trouch.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import fcntl
import array
import ctypes
import struct

from webiopi.utils.version import PYTHON_MAJOR
from webiopi.devices.bus import Bus

# from spi/spidev.h
_IOC_NRBITS   =  8
_IOC_TYPEBITS =  8
_IOC_SIZEBITS = 14
_IOC_DIRBITS  =  2

_IOC_NRSHIFT    = 0
_IOC_TYPESHIFT  = (_IOC_NRSHIFT+_IOC_NRBITS)
_IOC_SIZESHIFT  = (_IOC_TYPESHIFT+_IOC_TYPEBITS)
_IOC_DIRSHIFT   = (_IOC_SIZESHIFT+_IOC_SIZEBITS)

_IOC_NONE   = 0
_IOC_WRITE  = 1
_IOC_READ   = 2

def _IOC(direction,t,nr,size):
    return (((direction)  << _IOC_DIRSHIFT) |
            ((size) << _IOC_SIZESHIFT) |
            ((t) << _IOC_TYPESHIFT) |
            ((nr)   << _IOC_NRSHIFT))
def _IOR(t, number, size):
    return _IOC(_IOC_READ, t, number, size)
def _IOW(t, number, size):
    return _IOC(_IOC_WRITE, t, number, size)

SPI_CPHA        = 0x01
SPI_CPOL        = 0x02

SPI_MODE_0      = (0|0) 
SPI_MODE_1      = (0|SPI_CPHA)
SPI_MODE_2      = (SPI_CPOL|0)
SPI_MODE_3      = (SPI_CPOL|SPI_CPHA)

# does not work
# SPI_CS_HIGH     = 0x04
# SPI_LSB_FIRST   = 0x08
# SPI_3WIRE       = 0x10
# SPI_LOOP        = 0x20
# SPI_NO_CS       = 0x40
# SPI_READY       = 0x80

SPI_IOC_MAGIC   = ord('k')

def SPI_IOC_MESSAGE(count):
    return _IOW(SPI_IOC_MAGIC, 0, count)

# Read / Write of SPI mode (SPI_MODE_0..SPI_MODE_3)
SPI_IOC_RD_MODE             = _IOR(SPI_IOC_MAGIC, 1, 1)
SPI_IOC_WR_MODE             = _IOW(SPI_IOC_MAGIC, 1, 1)

# Read / Write SPI bit justification
# does not work
# SPI_IOC_RD_LSB_FIRST        = _IOR(SPI_IOC_MAGIC, 2, 1)
# SPI_IOC_WR_LSB_FIRST        = _IOW(SPI_IOC_MAGIC, 2, 1)

# Read / Write SPI device word length (1..N)
SPI_IOC_RD_BITS_PER_WORD    = _IOR(SPI_IOC_MAGIC, 3, 1)
SPI_IOC_WR_BITS_PER_WORD    = _IOW(SPI_IOC_MAGIC, 3, 1)

# Read / Write SPI device default max speed hz
SPI_IOC_RD_MAX_SPEED_HZ     = _IOR(SPI_IOC_MAGIC, 4, 4)
SPI_IOC_WR_MAX_SPEED_HZ     = _IOW(SPI_IOC_MAGIC, 4, 4)

class SPI(Bus):
    def __init__(self, chip=0, mode=0, bits=8, speed=0):
        Bus.__init__(self, "SPI", "/dev/spidev0.%d" % chip)
        self.chip = chip

        val8 = array.array('B', [0])
        val8[0] = mode
        if fcntl.ioctl(self.fd, SPI_IOC_WR_MODE, val8):
            raise Exception("Cannot write SPI Mode")
        if fcntl.ioctl(self.fd, SPI_IOC_RD_MODE, val8):
            raise Exception("Cannot read SPI Mode")
        self.mode = struct.unpack('B', val8)[0]
        assert(self.mode == mode)

        val8[0] = bits
        if fcntl.ioctl(self.fd, SPI_IOC_WR_BITS_PER_WORD, val8):
            raise Exception("Cannot write SPI Bits per word")
        if fcntl.ioctl(self.fd, SPI_IOC_RD_BITS_PER_WORD, val8):
            raise Exception("Cannot read SPI Bits per word")
        self.bits = struct.unpack('B', val8)[0]
        assert(self.bits == bits)

        val32 = array.array('I', [0])
        if speed > 0:
            val32[0] = speed
            if fcntl.ioctl(self.fd, SPI_IOC_WR_MAX_SPEED_HZ, val32):
                raise Exception("Cannot write SPI Max speed")
        if fcntl.ioctl(self.fd, SPI_IOC_RD_MAX_SPEED_HZ, val32):
            raise Exception("Cannot read SPI Max speed")
        self.speed = struct.unpack('I', val32)[0]
        assert((self.speed == speed) or (speed == 0))
    
    def __str__(self):
        return "SPI(chip=%d, mode=%d, speed=%dHz)" % (self.chip, self.mode, self.speed)
        
    def xfer(self, txbuff=None):
        length = len(txbuff)
        if PYTHON_MAJOR >= 3:
            _txbuff = bytes(txbuff)
            _txptr = ctypes.create_string_buffer(_txbuff)
        else:
            _txbuff = str(bytearray(txbuff))
            _txptr = ctypes.create_string_buffer(_txbuff)
        _rxptr = ctypes.create_string_buffer(length)
        
        data = struct.pack("QQLLHBBL",  #64 64 32 32 16 8 8 32 b = 32B
                    ctypes.addressof(_txptr),
                    ctypes.addressof(_rxptr),
                    length,
                    self.speed,
                    0, #delay
                    self.bits,
                    0, # cs_change,
                    0  # pad
                    )
        
        fcntl.ioctl(self.fd, SPI_IOC_MESSAGE(len(data)), data)
        _rxbuff = ctypes.string_at(_rxptr, length)
        return bytearray(_rxbuff)
        