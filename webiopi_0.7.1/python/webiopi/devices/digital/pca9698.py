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
#   1.0    2014/04/25    Initial release.
#
#   Config parameters
#
#   - slave         7 bit       I2C slave address
#   - invert_oe     yes, no     Invert OE pin 
#   - outconf       8 bit       Value of the OUTCONF register
#
#   Usage remarks
#
#   - Digital I/O channels are bound to the GPIOPort class
#   - This driver works only with the "banks" extension of the GPIOPort class
#   - Reading of output channels retrieves OPx register values
#   - Some peformance optimizations have been incorporated due to the high
#     number of channels in order to avoid excessive I2C bus calls
#   - The polarity inversion and interrupt masking functions are currently
#     not suppoprted
#   - The GPIO all call and the all banks control functions are currently
#     not supported 
#

from webiopi.utils.types import toint
from webiopi.utils.types import str2bool
from webiopi.devices.i2c import I2C
from webiopi.devices.digital import GPIOPort

class PCA9698(GPIOPort, I2C):

#---------- Constants and definitons ----------

    FUNCTIONS = []          # Needed for performance improvements
    INPUTMASK = 0           # dito
    
    # I2C Registers (currently unused ones are commented out)
    IP0         = 0x00      # IP0 input port (read only) register address
                            # IP1-4 are sequential from 0x01 to 0x04
    OP0         = 0x08      # OP0 output port (write/read) register address
                            # OP1-4 are sequential from 0x09 to 0x0C
    #PI0        = 0x10      # PI0 polarity inversion (write/read) register address
                            # PI1-4 are sequential from 0x11 to 0x14
    IOC0        = 0x18      # IOC0 I/O configuration register address
                            # IOC1-4 are sequential from 0x19 to 0x1C                            
                            # direction control values are input=1 output=0
    #MSK0       = 0x20      # MSK0 mask interrupt (write/read) register address
                            # MSK1-4 are sequential from 0x21 to 0x24
    OUTCONF      = 0x28     # Output structure configuration register address
    #ALLBNK      = 0x29     # Control all banks register address
    MODE         = 0x2A     # Mode selection register address

    # Flags (currently unused ones are commented out)    
    FLAG_AUTOINC  = 1 << 7  # Address bit to be set for address autoincrement
    FLAG_OEPOLHI  = 1       # OEPOL bit to be set for OE to be active high
    #FLAG_IOACON   = 1 << 3  # IOAC bit to be set to activate GPIO ALL CALL
                            
    # Constants
    CHANNELS      = 40      # This chip has 40 I/O ports organized as 
    BANKS         = 5       # 5 banks (@8bit each)

    # Defaults
    VAL_MODEDEF  = 1 << 1   # MODE default values


#---------- Class initialisation ----------
         
    def __init__(self, slave=0x20, invert_oe=False, outconf=0xFF):
        # Check parameter sanity
        oconf = toint(outconf)
        if oconf != 0xFF:
            if not oconf in range(0, 0xFF):
                raise ValueError("outconf value %d out of range [%d..%d]" % (oconf, 0x00, 0xFE))

        # Go for it
        I2C.__init__(self, toint(slave))
        GPIOPort.__init__(self, self.CHANNELS, self.BANKS)
        
        iv_oe = str2bool(invert_oe)
        if iv_oe:
            self.writeRegister(self.MODE, (self.VAL_MODEDEF | self.FLAG_OEPOLHI))
        else:
            self.writeRegister(self.MODE, self.VAL_MODEDEF)
            
        self.writeRegister(self.OUTCONF, oconf)
        self.reset()
        

#---------- Abstraction framework contracts ----------
              
    def __str__(self):
        return "PCA9698(slave=0x%02X)" % self.slave


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
        
        (addr, mask) = self.__getChannel__(self.IOC0, channel) 
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
        ipdata = self.readRegisters((self.FLAG_AUTOINC | self.IP0), self.BANKS)
        ipvalue = 0
        for i in range(self.BANKS):
            ipvalue |= ipdata[i] << 8*i
            
        opdata = self.readRegisters((self.FLAG_AUTOINC | self.OP0), self.BANKS)
        opvalue = 0
        for i in range(self.BANKS):
            opvalue |= opdata[i] << 8*i
        
        (ipmask, opmask) = self.__getFunctionMasks__()    
        return (ipvalue & ipmask) | (opvalue & opmask)

    def __portWrite__(self, value):
        data = bytearray(self.BANKS)        
        for i in range(self.BANKS):
            data[i] = (value >> 8*i) & 0xFF
        self.writeRegisters((self.FLAG_AUTOINC | self.OP0), data)


#---------- Device features ----------

    def reset(self):
        self.__resetFunctions__()
        self.__resetOutputs__()
  

#---------- Local helpers ----------

    def __resetFunctions__(self):
        # Default is to have all ports as input
        self.writeRegisters((self.FLAG_AUTOINC | self.IOC0), bytearray([0xFF for i in range (self.BANKS)]))
        self.FUNCTIONS = [self.IN for i in range(self.CHANNELS)]
        self.__updateInputMask__()

    def __resetOutputs__(self):
        # Default is to have all output latches set to 0
        self.writeRegisters((self.FLAG_AUTOINC | self.OP0), bytearray(self.BANKS))

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

        

