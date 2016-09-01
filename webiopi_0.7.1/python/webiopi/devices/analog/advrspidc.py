#   Copyright 2016 Andreas Riegg - t-h-i-n-x.net
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
#   0.9    2016-01-30    Initial release.
#
#   Config parameters
#
#   - chip     Integer   Value of the SPI CS address, valid values
#                        are 0 and 1. Default value is 0.
#
#   - vref     Float     Value of the analog reference voltage. Inherited
#                        from ADC abstraction but has no real meaning here.
#                        Used default value is 5.0.
#
#   - chips    Integer   Number of chips in the daisy chain, valid values
#                        are 1 and above. Default value is 1.
#
#
#   Usage remarks
#
#   - The specified parameter "chips" must exactly match the number of chips
#     in the chain.
#
#   - This driver supports only identical type chips in a single chain
#
#   Implementation remarks
#
#   - This driver supports only the SPI interface of the chips.
#
#   - This driver only works for "daisy-chained" SPI chips. See the chips spec
#     how the wiring should look like.
#
#   - As the SPI interface of all ADxxxx chips is write-only and does not allow to
#     to read back the register values, those are cached in the driver to still
#     allow reading them.
#
#

from webiopi.utils.types import toint
from webiopi.devices.spi import SPI
from webiopi.devices.analog import DAC
from webiopi.utils.logger import debug, printBytes

class ADVRSPIDC(DAC, SPI):

#---------- Class initialisation ----------

    def __init__(self, chip, vref, channelCount, resolution, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        DAC.__init__(self, toint(channelCount), toint(resolution), float(vref))
        self.name = name
        self.values = [0 for i in range(toint(channelCount))]

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(chip=%d)(chips=%d)(slice=%d)" %  (self.name, self.chip, self.chips, self.slice)

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.values[channel]


class ADVRSPIDCMULTI(ADVRSPIDC):

#---------- Class initialisation ----------

    def __init__(self, chip, vref, channelCount, resolution, name, chipsCount):
        ADVRSPIDC.__init__(self, chip, vref, channelCount*chipsCount, resolution, name)
        self.chips = chipsCount
        self.slice = channelCount

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        #printBytes(self.values)

        self.values[channel] = value & 0xFF
        #printBytes(self.values)

        chipAddr = channel%self.slice
        addressString = (bin(chipAddr)[2:]).rjust(self.ADDRESS_BITS,'0')
        debug("Address=%s" % addressString)

        slotValues = self.values[chipAddr::self.slice]
        #printBytes(slotValues)
        slotValues.reverse()
        printBytes(slotValues)

        unpaddedNumberBits = (self.ADDRESS_BITS + 8) * self.chips
        debug("Unpadlength=%s" % unpaddedNumberBits)

        lastBit = (unpaddedNumberBits % 8)
        if lastBit > 0:
            padLength = 8 - lastBit
        else:
            padLength = 0
        debug("Padlength=%s" % padLength)

        padString = "".rjust(padLength,'0')
        debug("Padding=%s" % padString)

        for i in range(len(slotValues)):
            slotValues[i] = (bin(slotValues[i])[2:]).rjust(8,'0')
        bitSequence = ""
        for valueString in slotValues:
            bitSequence = bitSequence + addressString + valueString
        bitSequence = padString + bitSequence
        debug("Bitsequence=%s" % bitSequence)

        data = []
        for s in range (0, len(bitSequence), 8):
            data.append(int(bitSequence[s:s+8], 2))
        printBytes(data)

        self.writeBytes(bytearray(data))


class AD5204DC(ADVRSPIDCMULTI):

#---------- Constants and definitons ----------

    ADDRESS_BITS = 3

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0, chips=1):
        ADVRSPIDCMULTI.__init__(self, chip, vref, 4, 8, "AD5204DC", toint(chips))


class AD5263DC(ADVRSPIDCMULTI):

#---------- Constants and definitons ----------

    ADDRESS_BITS = 2

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0, chips=1):
        ADVRSPIDCMULTI.__init__(self, chip, vref, 4, 8, "AD5263DC", toint(chips))


class AD8403DC(ADVRSPIDCMULTI):

#---------- Constants and definitons ----------

    ADDRESS_BITS = 2

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0, chips=1):
        ADVRSPIDCMULTI.__init__(self, chip, vref, 4, 8, "AD8403DC", toint(chips))


class ADVRSPIDCSINGLE(ADVRSPIDC):

#---------- Class initialisation ----------

    def __init__(self, chip, vref, chips, resolution, name):
        ADVRSPIDC.__init__(self, chip, vref, chips, resolution, name)
        self.chips = chips
        self.slice = 1

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.values[channel] = value & 0xFF
        data = bytearray(self.values)
        #printBytes(data)
        data.reverse()
        #printBytes(data)
        self.writeBytes(data)


class AD5161DC(ADVRSPIDCSINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0, chips=1):
        ADVRSPIDCSINGLE.__init__(self, chip, vref, toint(chips), 8, "AD5161DC")


class AD5290DC(ADVRSPIDCSINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0, chips=1):
        ADVRSPIDCSINGLE.__init__(self, chip, vref, toint(chips), 8, "AD5290DC")





