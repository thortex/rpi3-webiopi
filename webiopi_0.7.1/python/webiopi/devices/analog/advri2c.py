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
#   0.9    2015-10-08    Initial release.
#   1.0    2015-10-09    I2C default address fixed. Comments and arbitrary
#                        channel read added.
#   1.1    2015-10-16    Added more chips of same vendor with 1 and 2 channels.
#   1.2    2015-11-11    Renamed filename and classes. Chips that provide a dual
#                        interface have an "...I" at the end of the class name.
#   1.3    2015-20-11    Aligned the comments with advrspi.py
#
#   Config parameters
#
#   - slave     8 bit    Value of the I2C slave address, valid values
#                        are in the range 0x2C to 0x2F (2 address bits) for most
#                        chips, exceptions apply.
#
#   - vref      Float    Value of the analog reference voltage. Inherited
#                        from ADC abstraction but has no real meaning here.
#
#   Usage remarks
#
#   - Some chips have a selectable I2C and SPI interface. To use the I2C
#     interface, their class name has a "...I" at the end.
#
#   - Some chips have a fixed slave address. For them, the slave parameter
#     is not available. For most others, it defaults to 0x2C.
#
#   Implementation remarks
#
#   - This driver supports only the I2C interface of the chips.
#
#   - This driver does currently not support the digital output pins
#     (O1, some have also O2) that are available in I2C mode for some chips.
#
#   - This driver does currently not support the software reset (RS) and
#     shutdown (SD) command bits that are available in I2C mode for some chips.
#


from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.analog import DAC


class ADVRI2C(DAC, I2C):

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(slave=0x%02X)" %  (self.name, self.slave)


class ADVRI2CMULTI(ADVRI2C):

#---------- Class initialisation ----------

    def __init__(self, slave, vref, channelCount, resolution, name):
        I2C.__init__(self, toint(slave))
        DAC.__init__(self, channelCount, resolution, float(vref))
        self.name = name

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        d = (channel << self.CHANNEL_OFFSET) & self.CHANNEL_MASK
        self.writeByte(d)
        return self.readByte()

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        d = bytearray(2)
        d[0] = (channel << self.CHANNEL_OFFSET) & self.CHANNEL_MASK
        d[1] = value & 0xFF
        self.writeBytes(d)


class AD5242(ADVRI2CMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b10000000
    CHANNEL_OFFSET = 7

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CMULTI.__init__(self, slave, vref, 2, 8, "AD5242")


class AD5243(ADVRI2CMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b10000000
    CHANNEL_OFFSET = 7

#---------- Class initialisation ----------

    def __init__(self, vref=5.0):
        ADVRI2CMULTI.__init__(self, 0x2F, vref, 2, 8, "AD5243")


class AD5248(ADVRI2CMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b10000000
    CHANNEL_OFFSET = 7

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CMULTI.__init__(self, slave, vref, 2, 8, "AD5248")


class AD5263I(ADVRI2CMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b01100000
    CHANNEL_OFFSET = 5

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CMULTI.__init__(self, slave, vref, 4, 8, "AD5263I")


class AD5282(ADVRI2CMULTI):

#---------- Constants and definitons ----------

    CHANNEL_MASK   = 0b10000000
    CHANNEL_OFFSET = 7

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CMULTI.__init__(self, slave, vref, 2, 8, "AD5282")


class ADVRI2CSINGLE(ADVRI2C):

#---------- Class initialisation ----------

    def __init__(self, slave, vref, resolution, name):
        I2C.__init__(self, toint(slave))
        DAC.__init__(self, 1, resolution, float(vref))
        self.name = name

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.readByte()

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        d = bytearray(2)
        d[0] = 0x00
        d[1] = value & 0xFF
        self.writeBytes(d)


class AD5161I(ADVRI2CSINGLE):

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CSINGLE.__init__(self, slave, vref, 8, "AD5161I")


class AD5241(ADVRI2CSINGLE):

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CSINGLE.__init__(self, slave, vref, 8, "AD5241")


class AD5245(ADVRI2CSINGLE):

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CSINGLE.__init__(self, slave, vref, 8, "AD5245")


class AD5280(ADVRI2CSINGLE):

#---------- Class initialisation ----------

    def __init__(self, slave=0x2C, vref=5.0):
        ADVRI2CSINGLE.__init__(self, slave, vref, 8, "AD5280")


class ADVRI2CSIMPLE(ADVRI2CSINGLE):

#---------- Class initialisation ----------

    def __init__(self, slave, vref, resolution, name):
        ADVRI2CSINGLE.__init__(self, slave, vref, resolution, name)

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.writeByte(value & 0xFF)


class AD5246(ADVRI2CSIMPLE):

#---------- Class initialisation ----------

    def __init__(self, vref=5.0):
        ADVRI2CSIMPLE.__init__(self, 0x2E, vref, 7, "AD5246")

class AD5247(ADVRI2CSIMPLE):

#---------- Class initialisation ----------

    def __init__(self, slave=0x2E, vref=5.0):
        ADVRI2CSIMPLE.__init__(self, slave, vref, 7, "AD5247")
