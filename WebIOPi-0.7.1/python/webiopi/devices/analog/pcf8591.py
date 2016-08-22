#   Copyright 2014 Eric Ptak - trouch.com
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
from webiopi.devices.analog import DAC, ADC


class PCF8591(DAC, I2C):
    def __init__(self, slave=0x48, vref=3.3):
        I2C.__init__(self, toint(slave))
        DAC.__init__(self, 5, 8, float(vref))
        self.daValue = 0
        
        
    def __str__(self):
        return "PCF8591(slave=0x%02X)" % self.slave
    
    def __family__(self):
        return [DAC.__family__(self), ADC.__family__(self)]

    def __command__(self, adChannel=0):
        d = bytearray(2)
        d[0]  = 0x40           # enable output
        d[0] |= adChannel & 0x03
        d[1]  = self.daValue
        return d
    

    def __analogRead__(self, channel, diff=False):
        if (channel == 0):
            return self.daValue
        else:
            self.writeBytes(self.__command__(channel-1))
            return self.readBytes(3)[2]
                
    
    def __analogWrite__(self, channel, value):
        if (channel == 0):
            self.daValue = value
            self.writeBytes(self.__command__())
