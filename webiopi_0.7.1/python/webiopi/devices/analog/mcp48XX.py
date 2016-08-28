#   Copyright 2013 Dagda Ltd.
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

class MCP48XX(SPI, DAC):
    def __init__(self, chip, channelCount, resolution, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        DAC.__init__(self, channelCount, resolution, 2.048)
        self.name = name
        self.buffered=False
        self.gain=False
        self.shutdown=True
        self.values = [0 for i in range(channelCount)]

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def int2bin(self,n,count):
        return "".join([str((n >> y) & 1 ) for y in range(count-1,-1,-1)])

    def __analogRead__(self, channel, diff=False):
        return self.values[channel]

    def __analogWriteShut__(self, channel):
        self.shutdown = True
        d = [0x00, 0x00]
        d[0] |= (channel & 0x01) << 7             # bit 15 = channel
        d[0] |= 0x00 << 6                         # bit 14 = ignored
        d[0] |= 0x00 << 5                         # bit 13 = gain
        d[0] |= (self.shutdown & 0x01) << 4       # bit 12 = shutdown
        d[0] |= 0x00                              # bits 8-11 = msb data
        d[1] |= 0x00                              # bits 0 - 7 = lsb data
        
        self.writeBytes(d)
        self.values[channel] = 0

    def __analogWrite__(self, channel, value):
        self.shutdown=False
        d = [0x00, 0x00]
        d[0] |= (channel & 0x01) << 7                     # bit 15 = channel
        d[0] |= (self.buffered & 0x01) << 6               # bit 14 = ignored
        d[0] |= (not self.gain & 0x01) << 5               # bit 13 = gain
        d[0] |= (not self.shutdown & 0x01) << 4           # bit 12 = shutdown
        d[0] |= value >> (self._analogResolution - 4)     # bits 8-11 = msb data
        d[1] |= ((value << (12-self._analogResolution)) & 0xFF) # bits 4 - 7 = lsb data (4802) bits 2-7 (4812) bits 0-7 (4822)                              # bits 0 - 3 = ignored                       
        
        self.writeBytes(d)
        self.values[channel] = value
       
class MCP4802(MCP48XX):
    def __init__(self, chip=0):
        MCP48XX.__init__(self, chip, 2, 8, "MCP4802")

class MCP4812(MCP48XX):
    def __init__(self, chip=0):
        MCP48XX.__init__(self, chip, 2, 10, "MCP4812")

class MCP4822(MCP48XX):
    def __init__(self, chip=0):
        MCP48XX.__init__(self, chip, 2, 12, "MCP4822")

