#   Copyright 2014 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2014/04/25    Initial release.
#
#   Config parameters
#
#   - slave         7 bit       I2C slave address
#   - prescale0     8 bit       Value of the PSC0 register
#   - prescale1     8 bit       Value of the PSC1 register
#   - ledmode       4 bit       Value of the LSEL register
#
#   Usage remarks
#
#   - PWM channels are bound to the PWM class
#   - PWM class frequency is bound to prescale channel 0 as PWM class
#     can handle currently only one frequency for all pwm channels
#   - Prescale/PWM frequencies are bound to the DAC class, Vref is not
#     used but must be set for correct DAC init. Fixed value of 1.0 is used.
#   - Prescale/PWM frequencies can be set by config options
#   - Initial LEDx output configuration is to use prescale 0 for LED0
#     and prescale 1 for LED1
#   - LEDx output mode configuration is bound to the GPIOPort class
#     using 4 GPIO output only ports (LED0 bits -> channel 0,1,
#     LED1 bits -> channel 2,3) and can be set additionally by
#     method setLedMode() at runtime or by config option during setup
#   - GPIO input functionality for LED0/1 using the input register
#     is bound also to the GPIOPort class using 2 GPIO intput only
#     ports (LED0 bit -> channel 4, LED1 bit -> channel 5)
#

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.analog import PWM, DAC
from webiopi.devices.digital import GPIOPort

class PCA9530(PWM, DAC, GPIOPort, I2C):

#---------- Constants and definitons ----------

    # I2C Registers (currently unused ones are commented out)
    INPUT    = 0x00
    PSC0     = 0x01
    PWM0     = 0x02
    PSC1     = 0x03
    PWM1     = 0x04
    LSEL     = 0x05

    # Flags and modes    
    FLAG_AI    = 1 << 4
    LED0_OFF   = LED1_OFF   = 0b00
    LED0_ON    = LED1_ON    = 0b01
    LED0_RATE0 = LED1_RATE0 = 0b10
    LED0_RATE1 = LED1_RATE1 = 0b11
   
    # Constants
    PWM_CHANNELS   = 2
    PWM_RESOLUTION = 8
    DAC_CHANNELS   = 2
    DAC_RESOLUTION = 8
    GPIO_CHANNELS  = 6
    GPIO_BANKS	   = 3
    VREF           = 1.0 # Unused but must be set for DAC class init, so 1.0 is used 

    # Defaults
    D_PWM0      = 0x80
    D_PWM1      = 0x80

#---------- Class initialisation ----------

    def __init__(self, slave=0x60, prescale0=0, prescale1=0, ledmode=0b1110):
        # Check parameter sanity
        pres0 = toint(prescale0)
        if not pres0 in range(0, 0xFF + 1):
            raise ValueError("prescale0 value %d out of range [%d..%d]" % (pres0, 0x00, 0xFF))
        
        pres1 = toint(prescale1)        
        if not pres1 in range(0, 0xFF + 1):
            raise ValueError("prescale1 value %d out of range [%d..%d]" % (pres1, 0x00, 0xFF))
        
        lmode = toint(ledmode)        
        if not lmode in range(0, 0x0F + 1):
            raise ValueError("ledmode value %d out of range [%d..%d]" % (lmode, 0x00, 0x0F))

        # Go for it
        I2C.__init__(self, toint(slave))
        PWM.__init__(self, self.PWM_CHANNELS, self.PWM_RESOLUTION, self.__calculateFrequency__(pres0))
        DAC.__init__(self, self.DAC_CHANNELS, self.DAC_RESOLUTION, self.VREF)
        GPIOPort.__init__(self, self.GPIO_CHANNELS, self.GPIO_BANKS)

        d = bytearray(5)
        d[0] = pres0
        d[1] = self.D_PWM0
        d[2] = pres1
        d[3] = self.D_PWM1
        d[4] = lmode | 0xF0
        self.writeRegisters((self.PSC0 | self.FLAG_AI), d)


#---------- Abstraction framework contracts ----------
        
    def __str__(self):
        return "PCA9530(slave=0x%02X)" % self.slave

    def __family__(self):
        return [PWM.__family__(self), DAC.__family__(self), GPIOPort.__family__(self)]


#---------- PWM abstraction related methods ----------

    def __pwmRead__(self, channel):
        addr = self.__getPwmChannelAddress__(channel)
        return self.readRegister(addr)
    
    def __pwmWrite__(self, channel, value):
        addr = self.__getPwmChannelAddress__(channel)
        self.writeRegister(addr, value)


#---------- DAC abstraction related methods ----------
    
    def __analogRead__(self, channel, diff):
        addr = self.__getDacChannelAddress__(channel)
        return self.readRegister(addr)
    
    def __analogWrite__(self, channel, value):
        # Check for channel 0 to update frequency for PWM class
        if channel == 0:
            self.frequency = self.__calculateFrequency__(value)
        addr = self.__getDacChannelAddress__(channel)
        self.writeRegister(addr, value)


#---------- GPIOPort abstraction related methods ----------

    def __getFunction__(self, channel):
        if  3 < channel < 6:
            return self.IN
        else:
            return self.OUT
   
    def __setFunction__(self, channel, func):
        # GPIO functions are fixed and can't be changed
        raise ValueError("Requested function not supported")
   
    def __digitalRead__(self, channel):
        mask = 1 << channel
        if  3 < channel < 6:
            d = self.__inputPortRead__() << 4
        else:
            d = self.__ledPortRead__()
        return (d & mask) == mask
    
    def __digitalWrite__(self, channel, value):
        if  3 < channel < 6:
            raise ValueError("Requested function not supported")
        else:
            mask = 1 << channel
            d = self.readRegister(self.LSEL) & 0x0F
            if value:
                d |= mask
            else:
                d &= ~mask
            self.writeRegister(self.LSEL, d | 0xF0)
       
    def __portRead__(self):
        return self.__ledPortRead__() | (self.__inputPortRead__ << 4)
   
    def __portWrite__(self, value):
        val = toint(value)        
        if not val in range(0, 0x0F + 1):
            raise ValueError("ledmode value %d out of range [%d..%d]" % (val, 0x00, 0x0F))
        self.writeRegister(self.LSEL, val | 0xF0)

        
#---------- Device configuration ----------

    def setLedMode(self, led0Mode, led1Mode):
        # Example: pca9530instance.setLedMode(PCA9530.LED0_ON, PCA9530.LED1_RATE0)
        led0m = toint(led0Mode)       
        if not led0m in range(0, 0x04):
            raise ValueError("led0Mode value %d out of range [%d..%d]" % (led0m, 0x00, 0x03))
        led1m = toint(led1Mode)        
        if not led1m in range(0, 0x04):
            raise ValueError("led1Mode value %d out of range [%d..%d]" % (led1m, 0x00, 0x03))

        ledmode = (led0m | led1m << 2) | 0xF0
        self.writeRegister(self.LSEL, ledmode)


#---------- Local helpers ----------

    def __getPwmChannelAddress__(self, channel):
        return int(self.PWM0 + channel * 2) 

    def __getDacChannelAddress__(self, channel):
        return int(self.PSC0 + channel * 2)

    def __calculateFrequency__(self, prescale):
        return 152.0 / (prescale + 1)

    def __ledPortRead__(self):
        return self.readRegister(self.LSEL) & 0x0F
    
    def __inputPortRead__(self):
        return self.readRegister(self.INPUT) & 0x03
    

