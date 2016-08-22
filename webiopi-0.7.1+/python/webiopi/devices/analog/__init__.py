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

from webiopi.decorators.rest import request, response
from webiopi.utils.types import M_JSON

class ADC():
    def __init__(self, channelCount, resolution, vref):
        self._analogCount = channelCount
        self._analogResolution = resolution
        self._analogMax = 2**resolution - 1
        self._analogRef = vref
    
    def __family__(self):
        return "ADC"

    def checkAnalogChannel(self, channel):
        if not 0 <= channel < self._analogCount:
            raise ValueError("Channel %d out of range [%d..%d]" % (channel, 0, self._analogCount-1))

    def checkAnalogValue(self, value):
        if not 0 <= value <= self._analogMax:
            raise ValueError("Value %d out of range [%d..%d]" % (value, 0, self._analogMax))
    
    @request("GET", "analog/count")
    @response("%d")
    def analogCount(self):
        return self._analogCount

    @request("GET", "analog/resolution")
    @response("%d")
    def analogResolution(self):
        return self._analogResolution
    
    @request("GET", "analog/max")
    @response("%d")
    def analogMaximum(self):
        return int(self._analogMax)
    
    @request("GET", "analog/vref")
    @response("%.2f")
    def analogReference(self):
        return self._analogRef
    
    def __analogRead__(self, channel, diff):
        raise NotImplementedError
    
    @request("GET", "analog/%(channel)d/integer")
    @response("%d")
    def analogRead(self, channel, diff=False):
        self.checkAnalogChannel(channel)
        return self.__analogRead__(channel, diff)
    
    @request("GET", "analog/%(channel)d/float")
    @response("%.2f")
    def analogReadFloat(self, channel, diff=False):
        return self.analogRead(channel, diff) / float(self._analogMax)
    
    @request("GET", "analog/%(channel)d/volt")
    @response("%.2f")
    def analogReadVolt(self, channel, diff=False):
        if self._analogRef == 0:
            raise NotImplementedError
        return self.analogReadFloat(channel, diff) * self._analogRef
    
    @request("GET", "analog/*/integer")
    @response(contentType=M_JSON)
    def analogReadAll(self):
        values = {}
        for i in range(self._analogCount):
            values[i] = self.analogRead(i)
        return values
            
    @request("GET", "analog/*/float")
    @response(contentType=M_JSON)
    def analogReadAllFloat(self):
        values = {}
        for i in range(self._analogCount):
            values[i] = float("%.2f" % self.analogReadFloat(i))
        return values
    
    @request("GET", "analog/*/volt")
    @response(contentType=M_JSON)
    def analogReadAllVolt(self):
        values = {}
        for i in range(self._analogCount):
            values[i] = float("%.2f" % self.analogReadVolt(i))
        return values
    
class DAC(ADC):
    def __init__(self, channelCount, resolution, vref):
        ADC.__init__(self, channelCount, resolution, vref)
    
    def __family__(self):
        return "DAC"
    
    def __analogWrite__(self, channel, value):
        raise NotImplementedError
    
    @request("POST", "analog/%(channel)d/integer/%(value)d")
    @response("%d")    
    def analogWrite(self, channel, value):
        self.checkAnalogChannel(channel)
        self.checkAnalogValue(value)
        self.__analogWrite__(channel, value)
        return self.analogRead(channel)
    
    @request("POST", "analog/%(channel)d/float/%(value)f")        
    @response("%.2f")    
    def analogWriteFloat(self, channel, value):
        self.analogWrite(channel, int(value * self._analogMax))
        return self.analogReadFloat(channel)
    
    @request("POST", "analog/%(channel)d/volt/%(value)f")        
    @response("%.2f")    
    def analogWriteVolt(self, channel, value):
        self.analogWriteFloat(channel, value /self._analogRef)
        return self.analogReadVolt(channel)
    

class PWM():
    def __init__(self, channelCount, resolution, frequency):
        self._pwmCount = channelCount
        self._pwmResolution = resolution
        self._pwmMax = 2**resolution - 1
        self.frequency = frequency
        self.period = 1.0/frequency
        
        # Futaba servos standard
        self.servo_neutral = 0.00152
        self.servo_travel_time = 0.0004
        self.servo_travel_angle = 45.0
        
        self.reverse = [False for i in range(channelCount)]
         
    def __family__(self):
        return "PWM"

    def checkPWMChannel(self, channel):
        if not 0 <= channel < self._pwmCount:
            raise ValueError("Channel %d out of range [%d..%d]" % (channel, 0, self._pwmCount-1))

    def checkPWMValue(self, value):
        if not 0 <= value <= self._pwmMax:
            raise ValueError("Value %d out of range [%d..%d]" % (value, 0, self._pwmMax))
    
    def __pwmRead__(self, channel):
        raise NotImplementedError
    
    def __pwmWrite__(self, channel, value):
        raise NotImplementedError
    
    @request("GET", "pwm/count")
    @response("%d")
    def pwmCount(self):
        return self._pwmCount

    @request("GET", "pwm/resolution")
    @response("%d")
    def pwmResolution(self):
        return self._pwmResolution
    
    @request("GET", "pwm/max")
    @response("%d")
    def pwmMaximum(self):
        return int(self._pwmMax)
    
    @request("GET", "pwm/%(channel)d/integer")
    @response("%d")
    def pwmRead(self, channel):
        self.checkPWMChannel(channel)
        return self.__pwmRead__(channel)
    
    @request("GET", "pwm/%(channel)d/float")
    @response("%.2f")
    def pwmReadFloat(self, channel):
        return self.pwmRead(channel) / float(self._pwmMax)
    
    @request("POST", "pwm/%(channel)d/integer/%(value)d")
    @response("%d")    
    def pwmWrite(self, channel, value):
        self.checkPWMChannel(channel)
        self.checkPWMValue(value)
        self.__pwmWrite__(channel, value)
        return self.pwmRead(channel)
    
    @request("POST", "pwm/%(channel)d/float/%(value)f")        
    @response("%.2f")    
    def pwmWriteFloat(self, channel, value):
        self.pwmWrite(channel, int(value * self._pwmMax))
        return self.pwmReadFloat(channel)
    
    def getReverse(self, channel):
        self.checkChannel(channel)
        return self.reverse[channel]
    
    def setReverse(self, channel, value):
        self.checkChannel(channel)
        self.reverse[channel] = value
        return value
    
    def RatioToAngle(self, value):
        f = value
        f *= self.period
        f -= self.servo_neutral
        f *= self.servo_travel_angle
        f /= self.servo_travel_time
        return f

    def AngleToRatio(self, value):
        f = value
        f *= self.servo_travel_time
        f /= self.servo_travel_angle
        f += self.servo_neutral
        f /= self.period
        return f
    
    @request("GET", "pwm/%(channel)d/angle")
    @response("%.2f")
    def pwmReadAngle(self, channel):
        f = self.pwmReadFloat(channel)
        f = self.RatioToAngle(f)
        if self.reverse[channel]:
            f = -f
        else:
            f = f
        return f
        
    @request("POST", "pwm/%(channel)d/angle/%(value)f")
    @response("%.2f")
    def pwmWriteAngle(self, channel, value):
        if self.reverse[channel]:
            f = -value
        else:
            f = value
        f = self.AngleToRatio(f)
        self.pwmWriteFloat(channel, f)
        return self.pwmReadAngle(channel)

    @request("GET", "pwm/*")
    @response(contentType=M_JSON)
    def pwmWildcard(self):
        values = {}
        for i in range(self._pwmCount):
            val = self.pwmReadFloat(i)
            values[i] = {}
            values[i]["float"] = float("%.2f" % val)
            values[i]["angle"] = float("%.2f" % self.RatioToAngle(val))
        return values
    
DRIVERS = {}
DRIVERS["ads1x1x"] = ["ADS1014", "ADS1015", "ADS1114", "ADS1115"]
DRIVERS["mcp3x0x"] = ["MCP3002", "MCP3004", "MCP3008", "MCP3204", "MCP3208"]
DRIVERS["mcp4725"] = ["MCP4725"]
DRIVERS["mcp48XX"] = ["MCP4802", "MCP4812", "MCP4822"]
DRIVERS["mcp492X"] = ["MCP4921", "MCP4922"]
DRIVERS["pca9685"] = ["PCA9685"]
DRIVERS["pcf8591"] = ["PCF8591"]
