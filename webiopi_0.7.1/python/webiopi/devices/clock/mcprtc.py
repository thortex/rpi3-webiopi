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
#   1.0    2014-06-25    Initial release.
#   1.1    2014-08-27    Updated to match v1.1 of Clock implementation
#                        Added seq register access for __get ...
#
#   Config parameters
#
#   - control         8 bit       Value of the control register
#
#   Usage remarks
#
#   - The chip has a fixed slave address of 0x6F
#   - Setting alarms is currently not supported
#
#   - TBD writing security for 59 sec timeslot
#
#   Implementation remarks
#
#   - The driver has high similarity with the dsrtc one any may be merged
#     with it (or inherit from DSclock) sometime in future
#

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.clock import Clock
from webiopi.devices.memory import Memory
from webiopi.decorators.rest import request, response
from datetime import datetime, date, time


class MCP7940(I2C, Clock, Memory):

#---------- Constants and definitions ----------
    
    # Common I2C registers for all DSxxxx clock chips
    SEC  = 0x00  # Seconds register coded as 2-digit BCD
    MIN  = 0x01  # Minutes register coded as 2-digit BCD
    HRS  = 0x02  # Hours register coded as 2-digit BCD
    DOW  = 0x03  # Day of week register coded as 1-digit BCD
    DAY  = 0x04  # Day of month register coded as 2-digit BCD
    MON  = 0x05  # Months register coded as 2-digit BCD
    YRS  = 0x06  # Years register coded as 2-digit BCD
    CON  = 0x07  # Control register address
    RAM  = 0x20  # SRAM register address

    # Bit masks for registers
    SEC_MASK = 0b01111111
    MIN_MASK = 0b01111111
    HRS_MASK = 0b00111111
    DOW_MASK = 0b00000111
    DAY_MASK = 0b00111111
    MON_MASK = 0b00011111
    YRS_MASK = 0b11111111

    CON_MASK    = 0b10010011 # Control register mask
    CON_DEFAULT = 0b00000011 # Control register default value

    ST          = 0b10000000 # Start oscillator bit value/mask

#---------- Class initialisation ----------

    def __init__(self, control=None):
        I2C.__init__(self, 0x6F)
        Clock.__init__(self)
        Memory.__init__(self, 64)
        if control != None:
            con = toint(control)
            if not con in range(0, 0xFF + 1):
                raise ValueError("control value %d out of range [%d..%d]" % (con, 0x00, 0xFF))
            self.__setCon__(con)
        else:
            self.__setCon__(self.CON_DEFAULT)
            
        # Clock is stopped by default upon poweron, so start it
        self.start()


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "MCP7940"

    def __family__(self):
        return [Clock.__family__(self), Memory.__family__(self)]

    
#---------- Clock abstraction related methods ----------

    def __getSec__(self):
        data = self.readRegister(self.SEC)
        return self.BcdBits2Int(data & self.SEC_MASK)

    def __setSec__(self, value):
        # Keep ST bit unchanged
        secValue = self.Int2BcdBits(value)
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData & ~self.SEC_MASK) | (secValue & self.SEC_MASK))

    def __getMin__(self):
        data = self.readRegister(self.MIN)
        return self.BcdBits2Int(data & self.MIN_MASK)

    def __setMin__(self, value):
        self.writeRegister(self.MIN, self.Int2BcdBits(value & self.MIN_MASK))

    def __getHrs__(self):
        data = self.readRegister(self.HRS)
        return self.BcdBits2Int(data & self.HRS_MASK)

    def __setHrs__(self, value):
        # Keep 12/24 bit unchanged
        hrsValue = self.Int2BcdBits(value)
        hrsRegisterData = self.readRegister(self.HRS)
        self.writeRegister(self.HRS, (hrsRegisterData & ~self.HRS_MASK) | (hrsValue & self.HRS_MASK))

    def __getDay__(self):
        data = self.readRegister(self.DAY)
        return self.BcdBits2Int(data & self.DAY_MASK)

    def __setDay__(self, value):
        self.writeRegister(self.DAY, self.Int2BcdBits(value & self.DAY_MASK))

    def __getMon__(self):
        data = self.readRegister(self.MON)
        return self.BcdBits2Int(data & self.MON_MASK)

    def __setMon__(self, value):
        # Keep LP bit unchanged
        monValue = self.Int2BcdBits(value)
        monRegisterData = self.readRegister(self.MON)
        self.writeRegister(self.MON, (monRegisterData & ~self.MON_MASK) | (monValue & self.MON_MASK))

    def __getYrs__(self):
        data = self.readRegister(self.YRS)
        return 2000 + self.BcdBits2Int(data & self.YRS_MASK)

    def __setYrs__(self, value):
        self.writeRegister(self.YRS, self.Int2BcdBits((value - 2000) & self.YRS_MASK))

    def __getDow__(self):
        data = self.readRegister(self.DOW)
        return self.BcdBits2Int(data & self.DOW_MASK)

    def __setDow__(self, value):
        # Keep control bits unchanged
        dowValue = self.Int2BcdBits(value)
        dowRegisterData = self.readRegister(self.DOW)
        self.writeRegister(self.DOW, (dowRegisterData & ~self.DOW_MASK) | (dowValue & self.DOW_MASK))

#---------- Clock default re-implementations ----------
# Speed up performance by sequential register access
# Only provided for __getxxx__() methods as presevering bits of time
# registers within __setxxx__() methods would need too much reads before
# which will degrade speed improvement a lot. And, setting values of
# RTC chips occurs very seldom anyway.

    def __getDateTime__(self):
        data = self.readRegisters(self.SEC, 7)
        second = self.BcdBits2Int(data[0] & self.SEC_MASK)
        minute = self.BcdBits2Int(data[1] & self.MIN_MASK)
        hour   = self.BcdBits2Int(data[2] & self.HRS_MASK)
        day    = self.BcdBits2Int(data[4] & self.DAY_MASK)
        month  = self.BcdBits2Int(data[5] & self.MON_MASK)
        year   = self.BcdBits2Int(data[6] & self.YRS_MASK) + 2000
        return datetime(year, month, day, hour, minute, second)

    def __getDate__(self):
        data = self.readRegisters(self.DAY, 3)
        day    = self.BcdBits2Int(data[0] & self.DAY_MASK)
        month  = self.BcdBits2Int(data[1] & self.MON_MASK)
        year   = self.BcdBits2Int(data[2] & self.YRS_MASK) + 2000
        return date(year, month, day)

    def __getTime__(self):
        data = self.readRegisters(self.SEC, 3)
        second = self.BcdBits2Int(data[0] & self.SEC_MASK)
        minute = self.BcdBits2Int(data[1] & self.MIN_MASK)
        hour   = self.BcdBits2Int(data[2] & self.HRS_MASK)
        return time(hour, minute, second)


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
        # Set ST bit, keep sec value unchanged
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData | self.ST))      

    @request("POST", "run/stop")
    def stop(self):
        # Clear ST bit, keep sec value unchanged
        secRegisterData = self.readRegister(self.SEC)
        self.writeRegister(self.SEC, (secRegisterData & ~self.ST))      

#---------- Local helpers ----------

    def __getCon__(self):
        data = self.readRegister(self.CON)
        return (data & self.CON_MASK)

    def __setCon__(self, value):
        self.writeRegister(self.CON, (value & self.CON_MASK))
