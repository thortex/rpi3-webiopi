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
#   1.3    2014-11-13    Changed parameter order for writeMemoryBytes and
#                        optimized it.
#   1.4    2014-12-08    Simplified multiple read/write byte methods and
#                        made start/stop bounds checking more strict.
#                        Added REST mapping for multiple bytes reading.
#                        Made addressing scheme uniform for all slot types.
#
#   Usage remarks
#
#   - The smallest possible memory unit is 1 byte (8 bits)
#   - Addressed slots can be
#     - bits  ( 1 bit)
#     - bytes ( 8 bits)
#     - words (16 bits)
#     - longs (32 bits)
#   - All memory address slots are mapped strictly sequential in ascending
#     order like channel numbers starting at 0 with MSB first for non
#     single-bit slots. This results in the following address slot mapping:
#     |<- bit 0             bit 31 ->|
#     01010101010101010101010101010101
#     |byte 0| byte 1| byte 2| byte 3|
#     | -- word 0 -- | -- word 1 --  |
#     | ---------- long 0 ---------- |
#   - Where applicable, start and stop have the same meaning as range and
#     list slices in Python. Start is included, stop is excluded.
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
                position = 7 - j
                values[i*8 + j] = "%d" % ((valbyte & (1 << position)) >> position)
        return values

        # {
        #  "0": "0",
        #  "1": "0",
        #  "2": "0",
        #  "3": "1"
        #  "4": "0"
        #  "5": "0"
        #  "6": "1"
        #  "7": "0"
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

    @request("GET", "memory/bytes/%(bounds)s")
    @response(contentType=M_JSON)
    def memoryBytes(self, bounds):
        (start, stop) = bounds.split(",")
        start = toint(start)
        stop = toint(stop)
        values = {}
        byteValues = self.readMemoryBytes(start, stop)
        for i in range(start, stop):
            values[i] = "0x%02X" % byteValues[i - start]
        return values

        # {
        #  "1": "0x34",
        #  "2": "0xDE",
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
        maxCount = self.byteCount()
        if stop is None:
            stop = maxCount
        self.checkByteAddress(start)
        self.checkStopByteAddress(stop)
        byteValues = []
        if start > stop:
            raise ValueError("Stop address must be >= start address")
        for i in range(start, stop):
            byteValues.append(self.readMemoryByte(i))
        return byteValues

    def writeMemoryBytes(self, start=0, byteValues=[]):
        self.checkByteAddress(start)
        stop = start + len(byteValues)
        self.checkStopByteAddress(stop)
        i = 0
        for byte in byteValues: # do nothing if list is empty
            position = i + start
            self.writeMemoryByte(position, byte)
            i += 1


#---------- Memory abstraction contracts ----------
    
    def __readMemoryByte__(self, address):
        raise NotImplementedError

    def __writeMemoryByte__(self, address, value):
        raise NotImplementedError

#---------- Memory abstraction contracts with default implementations ---------

    def __readMemoryBit__(self, address):
        byteAddress, rawPosition = divmod(address, 8)
        bitPosition = 7 - rawPosition
        return (self.__readMemoryByte__(byteAddress) & (1 << bitPosition)) >> bitPosition

    def __writeMemoryBit__(self, address, value):
        byteAddress, rawPosition = divmod(address, 8)
        bitPosition = 7 - rawPosition
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

    def checkStopByteAddress(self, address):
        if not 0 <= address <= self.byteCount():
            raise ValueError("Stop byte address [%d] out of range [%d..%d]" % (address, 0, self.byteCount()))

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
DRIVERS["at24"] = ["EE24BASIC", "EE24X32", "EE24X64", "EE24X128", "EE24X256", "EE24X512", "EE24X1024_2"]

