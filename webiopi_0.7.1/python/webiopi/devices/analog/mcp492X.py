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
from webiopi.devices.spi import SPI
from webiopi.devices.analog import DAC

class MCP492X(SPI, DAC):
    def __init__(self, chip, channelCount, vref):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        DAC.__init__(self, channelCount, 12, float(vref))
        self.buffered=False
        self.gain=False
        self.shutdown=False
        self.values = [0 for i in range(channelCount)]

    def __str__(self):
        return "MCP492%d(chip=%d)" % (self._analogCount, self.chip)

    def __analogRead__(self, channel, diff=False):
        return self.values[channel]
        
    def __analogWrite__(self, channel, value):
        d = bytearray(2)
        d[0]  = 0
        d[0] |= (channel & 0x01) << 7
        d[0] |= (self.buffered & 0x01) << 6
        d[0] |= (not self.gain & 0x01) << 5
        d[0] |= (not self.shutdown & 0x01) << 4
        d[0] |= (value >> 8) & 0x0F
        d[1]  = value & 0xFF
        self.writeBytes(d)
        self.values[channel] = value

class MCP4921(MCP492X):
    def __init__(self, chip=0, vref=3.3):
        MCP492X.__init__(self, chip, 1)

class MCP4922(MCP492X):
    def __init__(self, chip=0, vref=3.3):
        MCP492X.__init__(self, chip, 2)

