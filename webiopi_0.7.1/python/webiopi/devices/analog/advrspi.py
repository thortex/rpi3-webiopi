#   Copyright 2015 Andreas Riegg - t-h-i-n-x.net
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
#   0.9    2015-11-11    Initial release. Works only for AD5263.
#   1.0    2015-11-20    Added many other ADVR SPI interface chips.
#
#   Config parameters
#
#   - chip     Integer   Value of the SPI CS address, valid values
#                        are 0 and 1.
#
#   - vref     Float     Value of the analog reference voltage. Inherited
#                        from ADC abstraction but has no real meaning here.
#
#   Usage remarks
#
#   - Some chips have a selectable I2C and SPI interface. To use the SPI
#     interface, their class name has a "...S" at the end.
#
#   Implementation remarks
#
#   - This driver supports only the SPI interface of the chips.
#
#   - As the SPI interface of all chips is write-only and does not allow to
#     to read back the register values, those are cached in the driver to still
#     allow reading them.
#
#

from webiopi.utils.types import toint
from webiopi.devices.spi import SPI
from webiopi.devices.analog import DAC


class ADVRSPI(DAC, SPI):

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(chip=%d)" %  (self.name, self.chip)


class ADVRSPIMULTI(ADVRSPI):

#---------- Class initialisation ----------

    def __init__(self, chip, vref, channelCount, resolution, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        DAC.__init__(self, channelCount, resolution, float(vref))
        self.name = name
        self.values = [0 for i in range(channelCount)]

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.values[channel]

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        d = bytearray(2)
        d[0] = channel & self.CHANNEL_MASK
        d[1] = value & 0xFF
        self.writeBytes(d)
        self.values[channel] = value


class AD5162(ADVRSPIMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000001

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 2, 8, "AD5162")


class AD5204(ADVRSPIMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000111

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 4, 8, "AD5204")


class AD5206(ADVRSPIMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000111

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 6, 8, "AD5206")


class AD5263S(ADVRSPIMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000011

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 4, 8, "AD5263S")


class AD8400(ADVRSPIMULTI):
# Special case, is a single channel chip but still does expect 2 address bits.

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000011

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 1, 8, "AD8400")


class AD8402(ADVRSPIMULTI):
# Special case, is a dual channel chip but still does expect 2 address bits.

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000011

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 2, 8, "AD8402")


class AD8403(ADVRSPIMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b00000011

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPIMULTI.__init__(self, chip, vref, 4, 8, "AD8403")


class ADVRSPISINGLE(ADVRSPI):

#---------- Class initialisation ----------

    def __init__(self, chip, vref, resolution, name):
        SPI.__init__(self, toint(chip), 0, 8, 10000000)
        DAC.__init__(self, 1, resolution, float(vref))
        self.name = name
        self.value = 0

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.value

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.writeByte(value & 0xFF)
        self.value = value


class AD5160(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 8, "AD5160")


class AD5161S(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 8, "AD5161S")


class AD5165(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 8, "AD5165")


class AD5200(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 8, "AD5200")


class AD5201(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 6, "AD5201")


class AD5290(ADVRSPISINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, vref=5.0):
        ADVRSPISINGLE.__init__(self, chip, vref, 8, "AD5290")





