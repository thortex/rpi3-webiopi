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

from webiopi.utils.types import M_JSON
from webiopi.utils.logger import debug
from webiopi.devices.digital import GPIOPort
from webiopi.decorators.rest import request, response
try:
    import _webiopi.GPIO as GPIO
except:
    pass

EXPORT = []

class NativeGPIO(GPIOPort):
    def __init__(self):
        GPIOPort.__init__(self, 54)
        self.export = range(54)
        self.post_value = True
        self.post_function = True
        self.gpio_setup = []
        self.gpio_reset = []
        
    def __str__(self):
        return "GPIO"
    
    def addGPIO(self, lst, gpio, params):
        gpio = int(gpio)
        params = params.split(" ")
        func = params[0].lower()
        if func == "in":
            func = GPIO.IN
        elif func == "out":
            func = GPIO.OUT
        else:
            raise Exception("Unknown function")
        
        value = -1
        if len(params) > 1:
            value = int(params[1])
        lst.append({"gpio": gpio, "func": func, "value": value})
    
    def addGPIOSetup(self, gpio, params):
        self.addGPIO(self.gpio_setup, gpio, params)
        
    def addGPIOReset(self, gpio, params):
        self.addGPIO(self.gpio_reset, gpio, params)
        
    def addSetups(self, gpios):
        for (gpio, params) in gpios:
            self.addGPIOSetup(gpio, params)

    def addResets(self, gpios):
        for (gpio, params) in gpios:
            self.addGPIOReset(gpio, params)
    
    def setup(self):
        for g in self.gpio_setup:
            gpio = g["gpio"]
            debug("Setup GPIO %d" % gpio)
            GPIO.setFunction(gpio, g["func"])
            if g["value"] >= 0 and GPIO.getFunction(gpio) == GPIO.OUT:
                GPIO.digitalWrite(gpio, g["value"])
    
    def close(self):
        for g in self.gpio_reset:
            gpio = g["gpio"]
            debug("Reset GPIO %d" % gpio)
            GPIO.setFunction(gpio, g["func"])
            if g["value"] >= 0 and GPIO.getFunction(gpio) == GPIO.OUT:
                GPIO.digitalWrite(gpio, g["value"])
        
    def checkDigitalChannelExported(self, channel):
        if not channel in self.export:
            raise GPIO.InvalidChannelException("Channel %d is not allowed" % channel)
        
    def checkPostingFunctionAllowed(self):
        if not self.post_function:
            raise ValueError("POSTing function to native GPIO not allowed")
    
    def checkPostingValueAllowed(self):
        if not self.post_value:
            raise ValueError("POSTing value to native GPIO not allowed")
    
    def __digitalRead__(self, channel):
        self.checkDigitalChannelExported(channel)
        return GPIO.digitalRead(channel)
    
    def __digitalWrite__(self, channel, value):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        GPIO.digitalWrite(channel, value)

    def __getFunction__(self, channel):
        self.checkDigitalChannelExported(channel)
        return GPIO.getFunction(channel)
    
    def __setFunction__(self, channel, value):
        self.checkDigitalChannelExported(channel)
        self.checkPostingFunctionAllowed()
        GPIO.setFunction(channel, value)
        
    def __portRead__(self):
        value = 0
        for i in self.export:
            value |= GPIO.digitalRead(i) << i
        return value 
            
    def __portWrite__(self, value):
        if len(self.export) < 54:
            for i in self.export:
                if GPIO.getFunction(i) == GPIO.OUT:
                    GPIO.digitalWrite(i, (value >> i) & 1)
        else:
            raise Exception("Please limit exported GPIO to write integers")
            
    @request("GET", "*")
    @response(contentType=M_JSON)
    def wildcard(self, compact=False):
        if compact:
            f = "f"
            v = "v"
        else:
            f = "function"
            v = "value"
            
        values = {}
        print(self.export)
        for i in self.export:
            if compact:
                func = GPIO.getFunction(i)
            else:
                func = GPIO.getFunctionString(i)
            values[i] = {f: func, v: int(GPIO.digitalRead(i))}
        return values

    
    @request("GET", "%(channel)d/pulse")
    def getPulse(self, channel):
        self.checkDigitalChannelExported(channel)
        self.checkDigitalChannel(channel)
        return GPIO.getPulse(channel)

    #thor
    @request("GET", "%(channel)d/freq")
    def getFrequency(self, channel):
        self.checkDigitalChannelExported(channel)
        self.checkDigitalChannel(channel)
        return GPIO.getFrequency(channel)
    
    @request("POST", "%(channel)d/sequence/%(args)s")
    @response("%d")
    def outputSequence(self, channel, args):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkDigitalChannel(channel)
        (period, sequence) = args.split(",")
        period = int(period)
        GPIO.outputSequence(channel, period, sequence)
        return int(sequence[-1])
        
    @request("POST", "%(channel)d/pulse/")
    def pulse(self, channel):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkDigitalChannel(channel)
        GPIO.pulse(channel)
        return "OK"
        
    @request("POST", "%(channel)d/pulseRatio/%(value)f")
    def pulseRatio(self, channel, value):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkDigitalChannel(channel)
        GPIO.pulseRatio(channel, value)
        return GPIO.getPulse(channel)

    #thor
    @request("POST", "%(channel)d/pulseFreq/%(value)f")
    def pulseFreq(self, channel, value):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkDigitalChannel(channel)
        GPIO.setFrequency(channel, value)
        return GPIO.getFrequency(channel)
        
    @request("POST", "%(channel)d/pulseAngle/%(value)f")
    def pulseAngle(self, channel, value):
        self.checkDigitalChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkDigitalChannel(channel)
        GPIO.pulseAngle(channel, value)
        return GPIO.getPulse(channel)
    
    # 
    # for hardware PWM control
    # 
    #thor
    @request("GET",  "%(channel)d/hwpwm/clock")
    def getHWPWMclockSource(self, channel):
        return GPIO.HWPWMgetClockSource()

    @request("POST", "%(channel)d/hwpwm/clock/%(src)s")
    def setHWPWMclockSource(self, channel, src):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetClockSource(src)
        return GPIO.HWPWMgetClockSource()

    @request("GET",  "%(channel)d/hwpwm/freq")
    def getHWPWMfrequency(self, channel):
        return GPIO.HWPWMgetFrequency()

    @request("POST", "%(channel)d/hwpwm/freq/%(value)f")
    def setHWPWMfrequency(self, channel, value):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetFrequency(value)
        return GPIO.HWPWMgetFrequency()

    @request("GET",  "%(channel)d/hwpwm/msmode")
    def getHWPWMmSMode(self, channel):
        return GPIO.HWPWMgetMSMode(channel)

    @request("POST", "%(channel)d/hwpwm/msmode/%(msmode)d")
    def setHWPWMmSMode(self, channel, msmode):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetMSMode(channel, msmode)
        return GPIO.HWPWMgetMSMode(channel)

    @request("GET",  "%(channel)d/hwpwm/polarity")
    def getHWPWMpolarity(self, channel):
        return GPIO.HWPWMgetPolarity(channel)

    @request("POST", "%(channel)d/hwpwm/polarity/%(polarity)d")
    def setHWPWMpolarity(self, channel, polarity):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetPolarity(channel, polarity)
        return GPIO.HWPWMgetPolarity(channel)

    @request("GET",  "%(channel)d/hwpwm/output")
    def getHWPWMoutput(self, channel):
        value = GPIO.HWPWMisEnabled(channel)
        if value == True:
            return "enable"
        else:
            return "disable"

    @request("POST", "%(channel)d/hwpwm/output/%(value)s")
    def setHWPWMoutput(self, channel, value):
        self.checkPostingValueAllowed()
        if value == "enable":
            GPIO.HWPWMenable(channel)
        elif value == "disable":
            GPIO.HWPWMdisable(channel)
        else:
            raise ValueError("Bad Function")
        return self.getHWPWMoutput(channel)

    @request("GET",  "%(channel)d/hwpwm/port")
    def get(self, channel):
        return GPIO.HWPWMgetPort(x)

    @request("POST", "%(channel)d/hwpwm/port/%(port)d")
    def setHWPWMport(self, channel, port):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetPort(channel, port)
        return GPIO.HWPWMgetPort(channel)

    @request("GET",  "%(channel)d/hwpwm/period")
    def getHWPWMperiod(self, channel):
        return GPIO.HWPWMgetPeriod(channel)

    @request("POST", "%(channel)d/hwpwm/period/%(period)d")
    def setHWPWMperiod(self, channel, period):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetPeriod(channel, period)
        return GPIO.HWPWMgetPeriod(channel)

    @request("GET",  "%(channel)d/hwpwm/duty")
    def getHWPWMDuty(self, channel):
        return GPIO.HWPWMgetDuty(channel)

    @request("POST", "%(channel)d/hwpwm/duty/%(duty)d")
    def setHWPWMDuty(self, channel, duty):
        self.checkPostingValueAllowed()
        GPIO.HWPWMsetDuty(channel, duty)
        return GPIO.HWPWMgetDuty(channel)
