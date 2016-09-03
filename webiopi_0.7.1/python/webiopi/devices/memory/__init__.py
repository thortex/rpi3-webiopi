#   Copyright 2014 Andreas Riegg - t-h-i-n-x.net
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
#
#   Changelog
#
#   1.0    2014-06-26    Initial release.
#   1.1    2014-08-28    Added bit access.
#   1.2    2014-08-31    Added NON-REST multiple read/write byte methods 
#                        to speed up direct Python access.
#
#   Usage remarks
#
#   - Memory address slots are mapped like channel numbers staring at 0
#     but MSB is kept left as normal Python integer numbers. For byte
#     0x79 (0b01111001) at address 0 acessing /bit/0 = 1 and /bit/7 = 0.
#   - The smallest possible memory unit is 1 byte
#   - Currently values can be
#     - bits  ( 1 bit)
#     - bytes ( 8 bits)
#     - words (16 bits)
#     - longs (32 bits)
#

from webiopi.decorators.rest import request, response
from webiopi.utils.types import toint, M_JSON

class Memory():

    def __init__(self, byteCount):
        self._byteCount = byteCount


#---------- Abstraction framework contracts ----------
        
    def __family__(self):
        return "Memory"

#---------- Memory abstraction REST implementation ----------
    
    @request("GET", "memory/bit/*")
    @response(contentType=M_JSON)
    def memoryBitWildcard(self):
        values = {}
        for i in range(self.byteCount()):
            valbyte = self.readMemoryByte(i)
            for j in range(8):
                values[i*8 + j] = "%d" % ((valbyte & (1 << j)) >> j)
        return values

        # {
        #  "0": "0",
        #  "1": "1",
        #  "2": "0",
        #  "3": "0"
        #  ...
        # }

    @request("GET", "memory/byte/*")
    @response(contentType=M_JSON)
    def memoryByteWildcard(self):
        values = {}
        byteValues = self.readMemoryBytes()
        for i in range(len(byteValues)):
            values[i] = "0x%02X" % byteValues[i]
        return values

        # {
        #  "0": "0x12",
        #  "1": "0x34",
        #  "2": "0xDE",
        #  "3": "0xFF"
        # }

    @request("GET", "memory/word/*")
    @response(contentType=M_JSON)
    def memoryWordWildcard(self):
        values = {}
        for i in range(self.wordCount()):
            values[i] = "0x%04X" % self.readMemoryWord(i)
        return values

        # {
        #   "0": "0x1234",
        #   "1": "0xDEFF"
        # }

    @request("GET", "memory/long/*")
    @response(contentType=M_JSON)
    def memoryLongWildcard(self):
        values = {}
        for i in range(self.longCount()):
            values[i] = "0x%08X" % self.readMemoryLong(i)
        return values

        # {
        #   "0": "0x1234DEFF"
        # }

    @request("GET", "memory/bit/count")
    @response("%d")
    def bitCount(self):
        return self._byteCount * 8

    @request("GET", "memory/byte/count")
    @response("%d")
    def byteCount(self):
        return self._byteCount

    @request("GET", "memory/word/count")
    @response("%d")
    def wordCount(self):
        return self._byteCount >> 1

    @request("GET", "memory/long/count")
    @response("%d")
    def longCount(self):
        return self._byteCount >> 2
        
    @request("GET", "memory/bit/%(address)s")
    @response("%d")
    def readMemoryBit(self, address):
        address = toint(address)
        self.checkBitAddress(address)
        return self.__readMemoryBit__(address)

    @request("POST", "memory/bit/%(address)s/%(value)s")
    @response("%d")
    def writeMemoryBit(self, address, value):
        address = toint(address)
        self.checkBitAddress(address)
        value = toint(value)
        self.checkBitValue(value)
        self.__writeMemoryBit__(address, value)
        return self.readMemoryBit(address)

    @request("GET", "memory/byte/%(address)s")
    @response("0x%02X")
    def readMemoryByte(self, address):
        address = toint(address)
        self.checkByteAddress(address)
        return self.__readMemoryByte__(address)

    @request("POST", "memory/byte/%(address)s/%(value)s")
    @response("0x%02X")
    def writeMemoryByte(self, address, value):
        address = toint(address)
        self.checkByteAddress(address)
        value = toint(value)
        self.checkByteValue(value)
        self.__writeMemoryByte__(address, value)
        return self.readMemoryByte(address)

    @request("GET", "memory/word/%(address)s")
    @response("0x%04X")
    def readMemoryWord(self, address):
        address = toint(address)
        self.checkWordAddress(address)
        return self.__readMemoryWord__(address)

    @request("POST", "memory/word/%(address)s/%(value)s")
    @response("0x%04X")
    def writeMemoryWord(self, address, value):
        address = toint(address)
        self.checkWordAddress(address)
        value = toint(value)
        self.checkWordValue(value)
        self.__writeMemoryWord__(address, value)
        return self.readMemoryWord(address)

    @request("GET", "memory/long/%(address)s")
    @response("0x%08X")
    def readMemoryLong(self, address):
        address = toint(address)
        self.checkLongAddress(address)
        return self.__readMemoryLong__(address)

    @request("POST", "memory/long/%(address)s/%(value)s")
    @response("0x%08X")
    def writeMemoryLong(self, address, value):
        address = toint(address)
        self.checkLongAddress(address)
        value = toint(value)
        self.checkLongValue(value)
        self.__writeMemoryLong__(address, value)
        return self.readMemoryLong(address)

#---------- Memory abstraction NON-REST implementation ----------

    def readMemoryBytes(self, start=0, stop=None):
        count = self.byteCount()
        byteValues = []
        if start >= count:
            return byteValues # empty result
        if start < 0:
            start = 0 # truncate silent
        if stop is None:
            stop = count # adjust silent
        if (stop - start) > count:
            stop = count # adjust silent
        for i in range(start, stop):
            byteValues.append(self.readMemoryByte(i))
        return byteValues

    def writeMemoryBytes(self, byteValues, start=0):
        count = self.byteCount()
        i = 0
        for byte in byteValues: # do nothing if list is empty
            position = i + start
            if position >= count:
                return # truncate silent
            if position < 0:
                pass # adjust silent
            else:
                self.writeMemoryByte(i + start, byte)
            i += 1


#---------- Memory abstraction contracts ----------
    
    def __readMemoryByte__(self, address):
        raise NotImplementedError

    def __writeMemoryByte__(self, address, value):
        raise NotImplementedError

#---------- Memory abstraction contracts default implementations

    def __readMemoryBit__(self, address):
        byteAddress, bitPosition = divmod(address, 8)
        return (self.__readMemoryByte__(byteAddress) & (1 << bitPosition)) >> bitPosition

    def __writeMemoryBit__(self, address, value):
        byteAddress, bitPosition = divmod(address, 8)
        changeMask = 1 << bitPosition
        byteValue = self.__readMemoryByte__(byteAddress)       
        if value:
            byteValue |= changeMask
        else:
            byteValue &= ~changeMask          
        self.__writeMemoryByte__(byteAddress, byteValue)

    def __readMemoryWord__(self, address):
        byte0 = self.__readMemoryByte__(address * 2)
        byte1 = self.__readMemoryByte__((address * 2) + 1)      
        return (byte0 << 8) + byte1

    def __writeMemoryWord__(self, address, value):
        byte0 = (value >> 8) & 0xFF
        byte1 = value & 0xFF
        self.__writeMemoryByte__(address * 2, byte0)
        self.__writeMemoryByte__((address * 2) + 1, byte1)

    def __readMemoryLong__(self, address):
        byte0 = self.__readMemoryByte__(address * 4)
        byte1 = self.__readMemoryByte__((address * 4) + 1)      
        byte2 = self.__readMemoryByte__((address * 4) + 2)      
        byte3 = self.__readMemoryByte__((address * 4) + 3)      
        return (byte0 << 24) + (byte1 << 16) + (byte2 << 8) + byte3

    def __writeMemoryLong__(self, address, value):
        byte0 = (value >> 24) & 0xFF
        byte1 = (value >> 16) & 0xFF
        byte2 = (value >>  8) & 0xFF
        byte3 = value & 0xFF
        self.__writeMemoryByte__(address * 4, byte0)
        self.__writeMemoryByte__((address * 4) + 1, byte1)
        self.__writeMemoryByte__((address * 4) + 2, byte2)
        self.__writeMemoryByte__((address * 4) + 3, byte3)


#---------- Value checks ----------
    
    def checkBitAddress(self, address):
        if not 0 <= address < self.byteCount() * 8:
            raise ValueError("Bit address [%d] out of range [%d..%d]" % (address, 0, (self.byteCount() * 8) - 1))

    def checkBitValue(self, value):
        if not value in range(2):
            raise ValueError("Bit value [%d] out of range [0..1]" % value)

    def checkByteAddress(self, address):
        if not 0 <= address < self.byteCount():
            raise ValueError("Byte address [%d] out of range [%d..%d]" % (address, 0, self.byteCount() - 1))

    def checkByteValue(self, value):
        if not value in range(0x00,0xFF + 1):
            raise ValueError("Byte value [0x%02X] out of range [0x%02X..0x%02X]" % (value, 0x00,0xFF))

    def checkWordAddress(self, address):
        if not 0 <= address < self.wordCount():
            raise ValueError("Word address [%d] out of range [%d..%d]" % (address, 0, (self.wordCount() - 1)))

    def checkWordValue(self, value):
        if not value in range(0x00,0xFFFF + 1):
            raise ValueError("Word value [0x%04X] out of range [0x%04X..0x%04X]" % (value, 0x00,0xFFFF))
                        
    def checkLongAddress(self, address):
        if not 0 <= address < self.longCount():
            raise ValueError("Long address [%d] out of range [%d..%d]" % (address, 0, (self.longCount() - 1)))

    def checkLongValue(self, value):
        if not value in range(0x00,0xFFFFFFFF + 1):
            raise ValueError("Long value [0x%08X] out of range [0x%08X..0x%08X]" % (value, 0x00,0xFFFFFFFF))
                        
                        
#---------- Driver lookup ----------
        
DRIVERS = {}
DRIVERS["filememory"] = ["PICKLEFILE"]
