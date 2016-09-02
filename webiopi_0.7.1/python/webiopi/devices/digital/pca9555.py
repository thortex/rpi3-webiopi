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
#   1.0    2014/08/20    Initial release.
#   1.1    2014/09/30    Added PCA9535 support and remarks on PCF8575.
#
#   Config parameters
#
#   - slave         7 bit       I2C slave address
#
#   Usage remarks
#
#   - Digital I/O channels are bound to the GPIOPort class
#   - This driver is derived as copy and modify from the PCA9698 driver. Future
#     releases may include a merge with the PCA9698 driver if appropriate
#   - Reading of output channels retrieves OPx register values
#   - Some peformance optimizations have been incorporated due to the high
#     number of channels in order to avoid excessive I2C bus calls
#   - The polarity inversion and interrupt masking functions are currently
#     not suppoprted
#   - This driver also supports the PCA9535, but this has not been tested so far
#   - This driver does definitely NOT work for the PCF8575 as this chip has no
#     I2C registers to access the I/O ports via specific register addresses
#

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.digital import GPIOPort

class PCA9555(GPIOPort, I2C):

#---------- Constants and definitons ----------

    FUNCTIONS = []          # Needed for performance improvements
    INPUTMASK = 0           # dito
    
    # I2C Registers (currently unused ones are commented out)
    IP0         = 0x00      # IP0 input port (read only) register address
                            # IP1 is sequential on 0x01
    OP0         = 0x02      # OP0 output port (write/read) register address
                            # OP1 is sequential on 0x03
    #PI0        = 0x04      # PI0 polarity inversion (write/read) register address
                            # PI1 is sequential on 0x05
    CP0         = 0x06      # CP0 I/O configuration register address
                            # CP1 is sequential on 0x07                            
                            # direction control values are input=1 output=0
                            
    # Constants
    CHANNELS      = 16      # This chip has 16 I/O ports organized as 
    BANKS         = 2       # 2 banks (@8bit each)
    OP_DEFAULT    = 0xFF    # Output port values default to 1
    CP_DEFAULT    = 0xFF    # Port configuration registers default to 1 (input)
    

#---------- Class initialisation ----------
         
    def __init__(self, slave=0x20):
        I2C.__init__(self, toint(slave))
        GPIOPort.__init__(self, self.CHANNELS)
        self.reset()
        

#---------- Abstraction framework contracts ----------
              
    def __str__(self):
        return "PCA9555(slave=0x%02X)" % self.slave


#---------- GPIOPort abstraction related methods ----------
            
    def __digitalRead__(self, channel):
        if self.FUNCTIONS[channel] == self.OUT:
            # Read output latches for output ports
            reg_base = self.OP0
        else:
            reg_base = self.IP0                          
        (addr, mask) = self.__getChannel__(reg_base, channel) 
        d = self.readRegister(addr)
        return (d & mask) == mask

    def __digitalWrite__(self, channel, value):
        (addr, mask) = self.__getChannel__(self.OP0, channel) 
        d = self.readRegister(addr)
        if value:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)
        
    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]
                                       
    def __setFunction__(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Requested function not supported")
        
        (addr, mask) = self.__getChannel__(self.CP0, channel) 
        d = self.readRegister(addr)
        if value == self.IN:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)
        
        self.FUNCTIONS[channel] = value
        self.__updateInputMask__()

    def __portRead__(self):
        # Read all IP_ and OP_ and mix them together according to the FUNCTIONS list
        ipdata = self.readRegisters(self.IP0, self.BANKS)
        ipvalue = 0
        for i in range(self.BANKS):
            ipvalue |= ipdata[i] << 8*i
            
        opdata = self.readRegisters(self.OP0, self.BANKS)
        opvalue = 0
        for i in range(self.BANKS):
            opvalue |= opdata[i] << 8*i
        
        (ipmask, opmask) = self.__getFunctionMasks__()    
        return (ipvalue & ipmask) | (opvalue & opmask)

    def __portWrite__(self, value):
        data = bytearray(self.BANKS)        
        for i in range(self.BANKS):
            data[i] = (value >> 8*i) & 0xFF
        self.writeRegisters(self.OP0, data)


#---------- Device features ----------

    def reset(self):
        self.__resetFunctions__()
        self.__resetOutputs__()
  

#---------- Local helpers ----------

    def __resetFunctions__(self):
        # Default is to have all ports as input
        self.writeRegisters(self.CP0, bytearray([self.CP_DEFAULT for i in range (self.BANKS)]))
        self.FUNCTIONS = [self.IN for i in range(self.CHANNELS)]
        self.__updateInputMask__()

    def __resetOutputs__(self):
        # Default is to have all output latches set to OP_DEFAULT
        self.writeRegisters(self.OP0, bytearray([self.OP_DEFAULT for i in range (self.BANKS)]))

    def __getAddress__(self, register, channel=0):
        # Registers (8bit) are in increasing sequential order
        return register + int(channel / 8)

    def __getChannel__(self, register, channel):
        self.checkDigitalChannel(channel)
        addr = self.__getAddress__(register, channel) 
        mask = 1 << (channel % 8)
        return (addr, mask)
            
    def __updateInputMask__(self):
        channels = self.digitalChannelCount
        self.INPUTMASK = 0
        for i in range (channels):
            if self.FUNCTIONS[i] == self.IN:
                self.INPUTMASK |= 1 << i

    def __getFunctionMasks__(self):
        channels = self.digitalChannelCount
        inputMask = self.INPUTMASK
        return (inputMask, (~inputMask & ((1 << channels) - 1) ))
        # & expression is necessary to avoid 2's complement problems with using
        # ~ on very large numbers

class PCA9535(PCA9555):        

#---------- Class initialisation ----------
         
    def __init__(self, slave=0x20):
        PCA9555.__init__(self, toint(slave))


#---------- Abstraction framework contracts ----------
              
    def __str__(self):
        return "PCA9535(slave=0x%02X)" % self.slave

