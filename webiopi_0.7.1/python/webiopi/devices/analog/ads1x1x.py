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

from time import sleep
from webiopi.utils.types import toint, signInteger
from webiopi.devices.i2c import I2C
from webiopi.devices.analog import ADC


class ADS1X1X(ADC, I2C):
    VALUE     = 0x00
    CONFIG    = 0x01
    LO_THRESH = 0x02
    HI_THRESH = 0x03
    
    CONFIG_STATUS_MASK  = 0x80
    CONFIG_CHANNEL_MASK = 0x70
    CONFIG_GAIN_MASK    = 0x0E
    CONFIG_MODE_MASK    = 0x01
    
    def __init__(self, slave, channelCount, resolution, name):
        I2C.__init__(self, toint(slave))
        ADC.__init__(self, channelCount, resolution, 4.096)
        self._analogMax = 2**(resolution-1)
        self.name = name
        
        config = self.readRegisters(self.CONFIG, 2)
        
        mode = 0 # continuous
        config[0] &= ~self.CONFIG_MODE_MASK
        config[0] |= mode
        
        gain = 0x1 # FS = +/- 4.096V
        config[0] &= ~self.CONFIG_GAIN_MASK
        config[0] |= gain << 1
        
        self.writeRegisters(self.CONFIG, config)
    
    def __str__(self):
        return "%s(slave=0x%02X)" % (self.name, self.slave)
        
    def __analogRead__(self, channel, diff=False):
        config = self.readRegisters(self.CONFIG, 2)
        config[0] &= ~self.CONFIG_CHANNEL_MASK
        if diff:
            config[0] |= channel << 4
        else:
            config[0] |= (channel + 4) << 4
        self.writeRegisters(self.CONFIG, config)
        sleep(0.001)
        d = self.readRegisters(self.VALUE, 2)
        value = (d[0] << 8 | d[1]) >> (16-self._analogResolution)
        return signInteger(value, self._analogResolution)


class ADS1014(ADS1X1X):
    def __init__(self, slave=0x48):
        ADS1X1X.__init__(self, slave, 1, 12, "ADS1014")

class ADS1015(ADS1X1X):
    def __init__(self, slave=0x48):
        ADS1X1X.__init__(self, slave, 4, 12, "ADS1015")

class ADS1114(ADS1X1X):
    def __init__(self, slave=0x48):
        ADS1X1X.__init__(self, slave, 1, 16, "ADS1114")

class ADS1115(ADS1X1X):
    def __init__(self, slave=0x48):
        ADS1X1X.__init__(self, slave, 4, 16, "ADS1115")

