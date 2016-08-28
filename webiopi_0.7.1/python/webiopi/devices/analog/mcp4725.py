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
from webiopi.devices.analog import DAC


class MCP4725(DAC, I2C):
    def __init__(self, slave=0x60, vref=3.3):
        I2C.__init__(self, toint(slave))
        DAC.__init__(self, 1, 12, float(vref))
        
    def __str__(self):
        return "MCP4725(slave=0x%02X)" % self.slave

    def __analogRead__(self, channel, diff=False):
        d = self.readBytes(3)
        value = (d[1] << 8 | d[2]) >> 4
        return value
        
    
    def __analogWrite__(self, channel, value):
        d = bytearray(2)
        d[0] = (value >> 8) & 0x0F
        d[1] = value & 0xFF
        self.writeBytes(d)