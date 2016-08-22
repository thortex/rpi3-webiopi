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

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.spi import SPI
from webiopi.devices.digital import GPIOPort

class MCP23XXX(GPIOPort):
    IODIR   = 0x00
    IPOL    = 0x01
    GPINTEN = 0x02
    DEFVAL  = 0x03
    INTCON  = 0x04
    IOCON   = 0x05
    GPPU    = 0x06
    INTF    = 0x07
    INTCAP  = 0x08
    GPIO    = 0x09
    OLAT    = 0x0A
    
    def __init__(self, channelCount):
        GPIOPort.__init__(self, channelCount)
        self.banks = int(channelCount / 8)
        
    def getAddress(self, register, channel=0):
        return register * self.banks + int(channel / 8)

    def getChannel(self, register, channel):
        self.checkDigitalChannel(channel)
        addr = self.getAddress(register, channel) 
        mask = 1 << (channel % 8)
        return (addr, mask)
    
    def __digitalRead__(self, channel):
        (addr, mask) = self.getChannel(self.GPIO, channel) 
        d = self.readRegister(addr)
        return (d & mask) == mask

    def __digitalWrite__(self, channel, value):
        (addr, mask) = self.getChannel(self.GPIO, channel) 
        d = self.readRegister(addr)
        if value:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)
        
    def __getFunction__(self, channel):
        (addr, mask) = self.getChannel(self.IODIR, channel) 
        d = self.readRegister(addr)
        return self.IN if (d & mask) == mask else self.OUT
        
    def __setFunction__(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Requested function not supported")

        (addr, mask) = self.getChannel(self.IODIR, channel) 
        d = self.readRegister(addr)
        if value == self.IN:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)

    def __portRead__(self):
        value = 0
        for i in range(self.banks):
            value |= self.readRegister(self.banks*self.GPIO+i) << 8*i
        return value
    
    def __portWrite__(self, value):
        for i in range(self.banks):
            self.writeRegister(self.banks*self.GPIO+i,  (value >> 8*i) & 0xFF)

class MCP230XX(MCP23XXX, I2C):
    def __init__(self, slave, channelCount, name):
        I2C.__init__(self, toint(slave))
        MCP23XXX.__init__(self, channelCount)
        self.name = name
        
    def __str__(self):
        return "%s(slave=0x%02X)" % (self.name, self.slave)

class MCP23008(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 8, "MCP23008")

class MCP23009(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 8, "MCP23009")

class MCP23017(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 16, "MCP23017")

class MCP23018(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 16, "MCP23018")

class MCP23SXX(MCP23XXX, SPI):
    SLAVE = 0x20
    
    WRITE = 0x00
    READ  = 0x01
    
    def __init__(self, chip, slave, channelCount, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        MCP23XXX.__init__(self, channelCount)
        self.slave = self.SLAVE
        iocon_value = 0x08 # Hardware Address Enable
        iocon_addr  = self.getAddress(self.IOCON)
        self.writeRegister(iocon_addr, iocon_value)
        self.slave = toint(slave)
        self.name = name

    def __str__(self):
        return "%s(chip=%d, slave=0x%02X)" % (self.name, self.chip, self.slave)

    def readRegister(self, addr):
        d = self.xfer([(self.slave << 1) | self.READ, addr, 0x00])
        return d[2]

    def writeRegister(self, addr, value):
        self.writeBytes([(self.slave << 1) | self.WRITE, addr, value])
    
class MCP23S08(MCP23SXX):
    def __init__(self, chip=0, slave=0x20):
        MCP23SXX.__init__(self, chip, slave, 8, "MCP23S08")

class MCP23S09(MCP23SXX):
    def __init__(self, chip=0, slave=0x20):
        MCP23SXX.__init__(self, chip, slave, 8, "MCP23S09")

class MCP23S17(MCP23SXX):
    def __init__(self, chip=0, slave=0x20):
        MCP23SXX.__init__(self, chip, slave, 16, "MCP23S17")

class MCP23S18(MCP23SXX):
    def __init__(self, chip=0, slave=0x20):
        MCP23SXX.__init__(self, chip, slave, 16, "MCP23S18")

