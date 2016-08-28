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
from webiopi.devices.analog import ADC

class MCP3X0X(SPI, ADC):
    def __init__(self, chip, channelCount, resolution, vref, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000)
        ADC.__init__(self, channelCount, resolution, float(vref))
        self.name = name
        self.MSB_MASK = 2**(resolution-8) - 1

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def __analogRead__(self, channel, diff):
        data = self.__command__(channel, diff)
        r = self.xfer(data)
        return ((r[1] & self.MSB_MASK) << 8) | r[2]
    
class MCP300X(MCP3X0X):
    def __init__(self, chip, channelCount, vref, name):
        MCP3X0X.__init__(self, chip, channelCount, 10, vref, name)

    def __command__(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1
        d[1] |= (not diff) << 7
        d[1] |= ((channel >> 2) & 0x01) << 6
        d[1] |= ((channel >> 1) & 0x01) << 5
        d[1] |= ((channel >> 0) & 0x01) << 4
        return d
        
class MCP3002(MCP300X):
    def __init__(self, chip=0, vref=3.3):
        MCP300X.__init__(self, chip, 2, vref, "MCP3002")

    def __analogRead__(self, channel, diff):
        data = self.__command__(channel, diff)
        r = self.xfer(data)

        # Format of return is
        # 1 empty bit
        # 1 null bit
        # 10 ADC bits
        return (r[0]<<14 | r[1]<<6 | r[2]>>2) & ((2**self._analogResolution)-1)

    def __command__(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1                                 #start bit
        d[1] |= (not diff) << 7                   #single/differntial input
        d[1] |= channel  << 6                     #channel select
        return d

class MCP3004(MCP300X):
    def __init__(self, chip=0, vref=3.3):
        MCP300X.__init__(self, chip, 4, vref, "MCP3004")
        
class MCP3008(MCP300X):
    def __init__(self, chip=0, vref=3.3):
        MCP300X.__init__(self, chip, 8, vref, "MCP3008")
        
class MCP320X(MCP3X0X):
    def __init__(self, chip, channelCount, vref, name):
        MCP3X0X.__init__(self, chip, channelCount, 12, vref, name)

    def __command__(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (channel >> 2) & 0x01
        d[1] |= ((channel >> 1) & 0x01) << 7
        d[1] |= ((channel >> 0) & 0x01) << 6
        return d
    
class MCP3204(MCP320X):
    def __init__(self, chip=0, vref=3.3):
        MCP320X.__init__(self, chip, 4, vref, "MCP3204")
        
class MCP3208(MCP320X):
    def __init__(self, chip=0, vref=3.3):
        MCP320X.__init__(self, chip, 8, vref, "MCP3208")
        
