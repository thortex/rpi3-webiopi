#   DS2408 initial part Copyright 2013 Stuart Marsden
#   DS2413 part and 2408 mods Copyright 2014 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2013/MAR/01    Initial release by Stuart
#   2.0    2014/APR/09    Added DS2413 and updated DS2408 for proper input levels
#                         Fixed deprecated __output__() call of DS2408
#   2.1    2014/APR/28    Changed __digitalRead__() to read output latches for
#                         output ports and optimized __portRead__() with INPUTMASK
#                         Made DS2413 as small as possible
#
#   Config parameters
#
#   - slave         String       1-wire slave address
#
#   Usage remarks
#
#   - Output latches of ports to be used as input must be set to 1 (FETs off)
#     to allow reading of high levels (and to avoid electrical shorts).  
#   - RSTZ pin of DS2408 must be tied to high otherwise writing an output port
#     will fail with an exception in writeOutput().
#


from webiopi.devices.onewire import OneWire
from webiopi.devices.digital import GPIOPort
#from webiopi.utils import logger

class DS2408(OneWire, GPIOPort):

#---------- Constants and definitons ----------
    
    FUNCTIONS = []          # Needed for performance improvements
    INPUTMASK = 0           # dito


#---------- Class initialisation ----------

    def __init__(self, slave=None, family=0x29, extra="2408", channelCount=8):
        OneWire.__init__(self, slave, family, extra)
        GPIOPort.__init__(self, channelCount)

        self. __resetFunctions__()
        self.__portWrite__(0xFF) # Turn off output transistors to allow reading


#---------- Abstraction framework contracts ----------
        
    def __str__(self):
        return "DS2408(slave=%s)" % self.slave

    
#---------- GPIOPort abstraction related methods ----------

    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]
      
    def __setFunction__(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Requested function not supported")
        self.FUNCTIONS[channel] = value
        if value == self.IN:
            self.__digitalWrite__(channel, 1) # Turn off output transistors to allow reading

    def __digitalRead__(self, channel):
        mask = 1 << channel
        if self.FUNCTIONS[channel] == self.OUT:
            # Read output latches for output ports
            d = self.__readPortLatches__()
        else:
            d = self.__readInputs__()
        if d != None:
            return (d & mask) == mask
        
    def __digitalWrite__(self, channel, value):
        mask = 1 << channel
        b = self.__readPortLatches__()
        if value:
            b |= mask
        else:
            b &= ~mask
        self.__writeOutput__(b)
       
    def __portWrite__(self, value):
        self.__writeOutput__(value)
        
    def __portRead__(self):
        ipdata = self.__readInputs__()
        opdata = self.__readPortLatches__()
        (ipmask, opmask) = self.__getFunctionMasks__()    
        return (ipdata & ipmask) | (opdata & opmask)


#---------- 1-wire access handling ----------
    
    def __readState__(self):
        try:
            with open("/sys/bus/w1/devices/%s/state" % self.slave, "rb") as f:
                data = f.read(1)
            # logger.info("rs: %s" % (ord(data)))
            return ord(data)
        except IOError:
            return -1

    def __readOutput__(self):
        try:
            with open("/sys/bus/w1/devices/%s/output" % self.slave, "rb") as f:
                data = f.read(1)
            # logger.info("ro: %s" % (ord(data)))
            return bytearray(data)[0]
        except IOError:
            return -1
      
    def __writeOutput__(self, value):
        # logger.info("wo: %s" % (value))
        try:
            with open("/sys/bus/w1/devices/%s/output" % self.slave, "wb") as f:
                f.write(bytearray([value]))
        except IOError:
                # logger.info("wo: exception")
                pass


#---------- Local helpers ----------
            
    def __readInputs__(self):
        return self.__readState__()

    def __readPortLatches__(self):
        return self.__readOutput__()
       
    def __resetFunctions__(self):
        # Default is to have all ports as input
        self.FUNCTIONS = [self.IN for i in range(self.digitalChannelCount)]
        self.__updateInputMask__()

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

            
class DS2413(DS2408):

#---------- Class initialisation ----------

    def __init__(self, slave=None):
        DS2408.__init__(self, slave, 0x3A, "2413", 2)


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS2413(slave=%s)" % self.slave


#---------- Local helpers ----------

    def __readInputs__(self):
        d = self.__readState__()
        portAInput =  d & (1 << 0)
        portBInput =  d & (1 << 2)
        return portAInput | (portBInput >> 1)

    def __readPortLatches__(self):
        d = self.__readState__()
        portALatchState = d & (1 << 1)
        portBLatchState = d & (1 << 3)
        return (portALatchState >> 1) | (portBLatchState >> 2)


