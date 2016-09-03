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
#   1.1    2014-08-17    Updated to match v1.1 of Clock implementation
#
#   Config parameters
#
#   - control         8 bit       Value of the control register
#
#   Usage remarks
#
#   - All chips have a fixed slave address of 0x68
#   - Driver uses sequential register access to speed up performance
#   - Temperature reading from DS3231 is currently not supported
#   - Setting alarms for DS1337 and DS3231 is currently not supported
#

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.clock import Clock
from webiopi.devices.memory import Memory
from webiopi.decorators.rest import request, response
from datetime import datetime, date, time


class DSclock(I2C, Clock):

#---------- Constants and definitions ----------
    
    # Common I2C registers for all DSxxxx clock chips
    SEC  = 0x00  # Seconds register coded as 2-digit BCD
    MIN  = 0x01  # Minutes register coded as 2-digit BCD
    HRS  = 0x02  # Hours register coded as 2-digit BCD
    DOW  = 0x03  # Day of week register coded as 1-digit BCD
    DAY  = 0x04  # Day of month register coded as 2-digit BCD
    MON  = 0x05  # Months register coded as 2-digit BCD
    YRS  = 0x06  # Years register coded as 2-digit BCD

    # Bit masks for common registers for all DSxxxx clock chips
    SEC_MASK = 0b01111111
    MIN_MASK = 0b01111111
    HRS_MASK = 0b00111111
    DOW_MASK = 0b00000111
    DAY_MASK = 0b00111111
    MON_MASK = 0b00011111
    YRS_MASK = 0b11111111


#---------- Class initialization ----------

    def __init__(self, control):
        I2C.__init__(self, 0x68)
        Clock.__init__(self)
        if control != None:
            con = toint(control)
            if not con in range(0, 0xFF + 1):
                raise ValueError("control value [%d] out of range [%d..%d]" % (con, 0x00, 0xFF))
            self.__setCon__(con)
        else:
            self.__setCon__(self.CON_DEFAULT)

    
#---------- Clock abstraction related methods ----------

    def __getSec__(self):
        data = self.readRegister(self.SEC)
        return self.BcdBits2Int(data & self.SEC_MASK)

    def __getMin__(self):
        data = self.readRegister(self.MIN)
        return self.BcdBits2Int(data & self.MIN_MASK)

    def __getHrs__(self):
        data = self.readRegister(self.HRS)
        return self.BcdBits2Int(data & self.HRS_MASK)

    def __getDay__(self):
        data = self.readRegister(self.DAY)
        return self.BcdBits2Int(data & self.DAY_MASK)

    def __getMon__(self):
        data = self.readRegister(self.MON)
        return self.BcdBits2Int(data & self.MON_MASK)

    def __getYrs__(self):
        data = self.readRegister(self.YRS)
        return 2000 + self.BcdBits2Int(data & self.YRS_MASK)

    def __getDow__(self):
        data = self.readRegister(self.DOW)
        return self.BcdBits2Int(data & self.DOW_MASK)

    def __setDow__(self, value):
        self.writeRegister(self.DOW, self.Int2BcdBits(value & self.DOW_MASK))

#---------- Clock default re-implementations ----------
# Speed up performance by sequential register access

    def __getDateTime__(self):
        data = self.readRegisters(self.SEC, 7)
        second = self.BcdBits2Int(data[0] & self.SEC_MASK)
        minute = self.BcdBits2Int(data[1] & self.MIN_MASK)
        hour   = self.BcdBits2Int(data[2] & self.HRS_MASK)
        day    = self.BcdBits2Int(data[4] & self.DAY_MASK)
        month  = self.BcdBits2Int(data[5] & self.MON_MASK)
        year   = self.BcdBits2Int(data[6] & self.YRS_MASK) + 2000
        return datetime(year, month, day, hour, minute, second)

    def __setDateTime__(self, aDatetime):
        self.checkYear(aDatetime.year)
        dow = self.__getDow__() # preserve current dow value
        data = bytearray(7)
        data[0] = self.Int2BcdBits(aDatetime.second & self.SEC_MASK)
        data[1] = self.Int2BcdBits(aDatetime.minute & self.MIN_MASK)
        data[2] = self.Int2BcdBits(aDatetime.hour   & self.HRS_MASK)
        data[3] = self.Int2BcdBits(dow              & self.DOW_MASK)
        data[4] = self.Int2BcdBits(aDatetime.day    & self.DAY_MASK)
        data[5] = self.Int2BcdBits(aDatetime.month  & self.MON_MASK)
        data[6] = self.Int2BcdBits((aDatetime.year - 2000)  & self.YRS_MASK)
        self.writeRegisters(self.SEC, data)

    def __getDate__(self):
        data = self.readRegisters(self.DAY, 3)
        day    = self.BcdBits2Int(data[0] & self.DAY_MASK)
        month  = self.BcdBits2Int(data[1] & self.MON_MASK)
        year   = self.BcdBits2Int(data[2] & self.YRS_MASK) + 2000
        return date(year, month, day)

    def __setDate__(self, aDate):
        self.checkYear(aDate.year)
        data = bytearray(3)
        data[0] = self.Int2BcdBits(aDate.day   & self.DAY_MASK)
        data[1] = self.Int2BcdBits(aDate.month & self.MON_MASK)
        data[2] = self.Int2BcdBits((aDate.year - 2000)  & self.YRS_MASK)
        self.writeRegisters(self.DAY, data)

    def __getTime__(self):
        data = self.readRegisters(self.SEC, 3)
        second = self.BcdBits2Int(data[0] & self.SEC_MASK)
        minute = self.BcdBits2Int(data[1] & self.MIN_MASK)
        hour   = self.BcdBits2Int(data[2] & self.HRS_MASK)
        return time(hour, minute, second)

    def __setTime__(self, aTime):
        data = bytearray(3)
        data[0] = self.Int2BcdBits(aTime.second & self.SEC_MASK)
        data[1] = self.Int2BcdBits(aTime.minute & self.MIN_MASK)
        data[2] = self.Int2BcdBits(aTime.hour   & self.HRS_MASK)
        self.writeRegisters(self.SEC, data)


#---------- Local helpers ----------

    def __getCon__(self):
        data = self.readRegister(self.CON)
        return (data & self.CON_MASK)

    def __setCon__(self, value):
        self.writeRegister(self.CON, (value & self.CON_MASK))

            
class DS1307(DSclock, Memory):

    CON         = 0x07       # Control register address
    RAM         = 0x08       # SRAM register address
    
    CON_MASK    = 0b10010011 # Control register mask
    CON_DEFAULT = 0b10000011 # Control register default value
                                      
    CH          = 0b10000000 # Clock halt bit value/mask


#---------- Class initialization ----------

    def __init__(self, control=None):
        DSclock.__init__(self, control)
        Memory.__init__(self, 56)
        # Clock is stopped by default upon poweron, so start it
        self.start()


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS1307"

    def __family__(self):
        return [Clock.__family__(self), Memory.__family__(self)]


#---------- Clock abstraction related methods ----------

    def __setSec__(self, value):
        # Keep CH bit unchanged
        secValue = self.Int2BcdBits(value)
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData & ~self.SEC_MASK) | (secValue & self.SEC_MASK))


#---------- Memory abstraction related methods ----------

    def __readMemoryByte__(self, address):
        return self.readRegister(self.RAM + address)

    def __writeMemoryByte__(self, address, value):
        self.writeRegister(self.RAM + address, value)

    def __readMemoryWord__(self, address):
        data = self.readRegisters(self.RAM + address * 2, 2)
        return (data[0] << 8) + data[1]
        
    def __writeMemoryWord__(self, address, value):
        data = bytearray(2)
        data[0] = (value >> 8) & 0xFF
        data[1] = value & 0xFF
        self.writeRegisters(self.RAM + address * 2, data)

    def __readMemoryLong__(self, address):
        data = self.readRegisters(self.RAM + address * 4, 4)
        return (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]

    def __writeMemoryLong__(self, address, value):
        data = bytearray(4)
        data[0] = (value >> 24) & 0xFF
        data[1] = (value >> 16) & 0xFF
        data[2] = (value >>  8) & 0xFF
        data[3] = value & 0xFF
        self.writeRegisters(self.RAM + address * 4, data)


#---------- Device features ----------

    @request("POST", "run/start")
    def start(self):
        # Clear CH bit, keep sec value unchanged
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData & ~self.CH))      

    @request("POST", "run/stop")
    def stop(self):
        # Set CH bit, keep sec value unchanged
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData | self.CH))      


class DS1338(DS1307):

    CON_MASK    = 0b10110011 # Control register mask
    CON_DEFAULT = 0b10110011 # Control register default value


#---------- Class initialization ----------

    def __init__(self, control=None):
        DS1307.__init__(self, control)


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS1338"

    
class DS1337(DSclock):

    CON         = 0x0E       # Control register address
    CON_MASK    = 0b10011111 # Control register mask
    CON_DEFAULT = 0b00011000 # Control register default value
    EOSC_       = 0b10000000 # Enable oscillator active low bit value/mask


#---------- Class initialization ----------

    def __init__(self, control=None):
        DSclock.__init__(self, control)


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS1337"


#---------- Device features ----------

    @request("POST", "run/start")
    def start(self):
        # Clear EOSC_ bit
        conRegisterData = self.__getCon__()
        self.__setCon__(conRegisterData & ~self.EOSC_)      

    @request("POST", "run/stop")
    def stop(self):
        # Set EOSC_ bit
        conRegisterData = self.__getCon__()
        self.__setCon__(conRegisterData | self.EOSC_)      


class DS3231(DSclock):

    CON         = 0x0E       # Control register address
    CON_MASK    = 0b11011111 # Control register mask
    CON_DEFAULT = 0b00011100 # Control register default value


#---------- Class initialization ----------

    def __init__(self, control=None):
        DSclock.__init__(self, control)


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS3231"




