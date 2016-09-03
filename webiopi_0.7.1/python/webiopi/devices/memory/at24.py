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
#   1.0    2014-11-12    Initial release.
#   1.1    2014-12-08    Updated to match v1.4 of Memory implementation
#
#   Config parameters
#
#   (- bus (tbd)     Integer     Number ot the I2C bus (tbd))
#   - slave         8 bit       Value of the I2C slave address, valid values
#                               are in the range 0x50 to 0x57 (3 address bits)
#   - writeTime     Integer     value of the write cycle in ms
#
#   - slots         Integer	Number of used slots, can be smaller than
#                               number of available slots.
#
#   Usage remarks
#
#   - Slave address defaults to 0x50 which is all address bits grounded. 
#
#   Implementation remarks
#
#   - This driver is implemented inspired by the at24 module of Linux. It supports
#     reading and writing of at24-type I2C EEPROMS. However, it is restricted
#     to chips that use 16 bit addressing like the "HAT" standard of the RPi.
#   - Writing supports single byte mode as well as page mode. Bit and byte writes 
#     use the byte write mode, all other writes use the page write mode.
#   - If write cycle timing problems occur for some chip the write cycle wait
#     time can be set via config parameter.
#   - Choosing a slot number smaller than the available number can improve speed a bit
#     if not all slots are really needed for chips with large capacity.
#   - The at24.c driver recommends to use generic chip names like "24c32". As Python
#     class names must start with letters the prefix "EE" was added to the class names
#     to be more self-explaining. The same applies to using "X" as wildcard placeholder
#     like in other drivers.
#   - This driver uses the default I2C bus at the moment. Addressing a dedicated I2C
#     bus (like I2C bus 0 for HAT's) requires an extension of class I2C which is tbd.
#

from time import sleep
from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.memory import Memory

I2CMAXBUFF = 1024

class EE24XXXX(I2C, Memory):

#---------- Class initialisation ----------

    def __init__(self, slave, byteCount, pageSize, writeTime, name):
        slave = toint(slave)
        if not slave in range(0x50, 0x57 + 1):
             raise ValueError("Slave value [0x%02X] out of range [0x%02X..0x%02X]" % (slave, 0x50, 0x57))
        I2C.__init__(self, slave)
        # Tbd: HAT uses I2C channel 0
        Memory.__init__(self, byteCount)
        self._pageSize = pageSize
        self._writeTime = toint(writeTime) / 1000
        self.name = name

#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "%s(slave=0x%02X)" % (self.name, self.slave)


#---------- Memory abstraction related methods ----------

    def __readMemoryByte__(self, address):
        (addrHigh, addrLow) = self.splitAddress(address)
        return self.read16Byte(addrHigh, addrLow)

    def __writeMemoryByte__(self, address, value):
        (addrHigh, addrLow) = self.splitAddress(address)
        self.write16Byte(addrHigh, addrLow, value)
        sleep(self._writeTime)

    def __readMemoryWord__(self, address):
        (addrHigh, addrLow) = self.splitAddress(address * 2)
        data = self.read16Bytes(addrHigh, addrLow, 2)
        return (data[0] << 8) + data[1]
        
    def __writeMemoryWord__(self, address, value):
        data = bytearray(2)
        data[0] = (value >> 8) & 0xFF
        data[1] = value & 0xFF
        self.writeMemoryBytes(address * 2, data)

    def __readMemoryLong__(self, address):
        (addrHigh, addrLow) = self.splitAddress(address * 4)
        data = self.read16Bytes(addrHigh, addrLow, 4)
        return (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]

    def __writeMemoryLong__(self, address, value):
        data = bytearray(4)
        data[0] = (value >> 24) & 0xFF
        data[1] = (value >> 16) & 0xFF
        data[2] = (value >>  8) & 0xFF
        data[3] = value & 0xFF
        self.writeMemoryBytes(address * 4, data)


#---------- Memory abstraction NON-REST re-implementation ----------
# Avoid EEPROM reading/writing for every byte, do this in sequential/page mode

    def readMemoryBytes(self, start=0, stop=None):
        maxCount = self.byteCount()
        if stop is None:
            stop = maxCount
        self.checkByteAddress(start)
        self.checkStopByteAddress(stop)
        byteValues = []
        if start >= stop:
            raise ValueError("Stop address must be >= start address")
        readCount = stop - start
        (addrHigh, addrLow) = self.splitAddress(start)
        return self.read16Bytes(addrHigh, addrLow, readCount)

    def writeMemoryBytes(self, start=0, byteValues=[]):
        self.checkByteAddress(start)
        stop = start + len(byteValues)
        self.checkStopByteAddress(stop)
        self.writeMemoryBytesPaged(start, byteValues)


#---------- Local helpers ----------

    def splitAddress(self, address):
        return (address >> 8, address & 0xFF)

    def writeMemoryBytesPaged(self, start, byteValues):
        pSize = self._pageSize
        firstPage = start // pSize
        lastPage = (start + len(byteValues) - 1) // pSize
        if firstPage == lastPage: # no page overlap, just write
            (addrHigh, addrLow) = self.splitAddress(start)
            self.write16Bytes(addrHigh, addrLow, byteValues)
            sleep(self._writeTime)
        else: # page overlap(s) occur, separate writing to page aligned chunks
            address = start
            for p in range(firstPage, lastPage+1):
                vStart = p * pSize - start
                if vStart < 0: # first chunk may be shorter
                    vStart = 0
                vStop = (p + 1) * pSize - start
                pageBytes = byteValues[vStart:vStop] 
                (addrHigh, addrLow) = self.splitAddress(address)
                self.write16Bytes(addrHigh, addrLow, pageBytes)
                address = (p + 1) * pSize # advance to next page
                sleep(self._writeTime)

        
#---------- I2C helpers, should be added to class I2C ----------

    def read16Byte(self, addrHigh, addrLow):
        self.writeBytes([addrHigh, addrLow])
        return self.readByte()

    def read16Bytes(self, addrHigh, addrLow, count):
        self.writeBytes([addrHigh, addrLow])
        if count < (I2CMAXBUFF + 1):
            return self.readBytes(count)
        else:
            byteValues = []
            remainingCount = count
            while remainingCount > I2CMAXBUFF:
                remainingCount = remainingCount - I2CMAXBUFF
                byteValues += self.readBytes(I2CMAXBUFF)
            byteValues += self.readBytes(remainingCount)
            return byteValues
            

    def write16Byte(self, addrHigh, addrLow, byte):
        self.writeBytes([addrHigh, addrLow, byte])
 
    def write16Bytes(self, addrHigh, addrLow, buff):
        # Todo: adjust to io timeout error so max buff size may be around 1024
        # Will be only necessary when EEPROM pageSize exceeds 1022 bytes.
        d = bytearray(len(buff)+2)
        d[0] = addrHigh
        d[1] = addrLow
        d[2:] = buff
        self.writeBytes(d)
        

class EE24BASIC(EE24XXXX):
# This class implements a basic configuration that should work for unknown chips:
# - Addressed capacity is 32k bits (-> smallest chip specified for RPi HATs)
# - write cycle time is 25 ms (default value used in at24.c kernel driver)
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=25):
        EE24XXXX.__init__(self, slave, 4096, 32, writeTime, "EE24BASIC")


class EE24X32(EE24XXXX):
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=4096):
        slots= toint(slots)
        if not slots in range(1, 4097):
             raise ValueError("Slots value [%d] out of range [1..4096]" % slots)
        EE24XXXX.__init__(self, slave, slots, 32, writeTime, "EE24X32")


class EE24X64(EE24XXXX):
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=8192):
        if not slots in range(1, 8193):
             raise ValueError("Slots value [%d] out of range [1..8192]" % slots)
        EE24XXXX.__init__(self, slave, slots, 32, writeTime, "EE24X64")


class EE24X128(EE24XXXX):
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=16384):
        if not slots in range(1, 16385):
             raise ValueError("Slots value [%d] out of range [1..16384]" % slots)
        EE24XXXX.__init__(self, slave, slots, 64, writeTime, "EE24X128")


class EE24X256(EE24XXXX):
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=32768):
        if not slots in range(1, 32769):
             raise ValueError("Slots value [%d] out of range [1..32768]" % slots)
        EE24XXXX.__init__(self, slave, slots, 64, writeTime, "EE24X256")


class EE24X512(EE24XXXX):
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=65536):
        if not slots in range(1, 65537):
             raise ValueError("Slots value [%d] out of range [1..65536]" % slots)
        EE24XXXX.__init__(self, slave, slots, 128, writeTime, "EE24X512")

    
class EE24X1024_2(EE24XXXX):
# Only supports half of the capacity (first block)
# Does not work in full capacity mode because block bit is coded in slave address!
# Each chip uses 2 I2C slave addresses, for full capacity this has to be implemented
# in a separate driver.
    
#---------- Class initialisation ----------

    def __init__(self, slave=0x50, writeTime=5, slots=65536):
        if not slots in range(1, 65537):
             raise ValueError("Slots value [%d] out of range [1..65536]" % slots)
        EE24XXXX.__init__(self, slave, slots, 128, writeTime, "EE24X1024_2")

