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
from webiopi.utils.types import M_JSON
from webiopi.devices.instance import deviceInstance
from webiopi.decorators.rest import request, response

class Pressure():
    def __init__(self, altitude=0, external=None):
        self.altitude = toint(altitude)
        if isinstance(external, str):
            self.external = deviceInstance(external)
        else:
            self.external = external
        
        if self.external != None and not isinstance(self.external, Temperature):
            raise Exception("external must be a Temperature sensor")

    def __family__(self):
        return "Pressure"

    def __getPascal__(self):
        raise NotImplementedError
    
    def __getPascalAtSea__(self):
        raise NotImplementedError
    
    @request("GET", "sensor/pressure/pa")
    @response("%d")
    def getPascal(self):
        return self.__getPascal__()
    
    @request("GET", "sensor/pressure/hpa")
    @response("%.2f")
    def getHectoPascal(self):
        return float(self.__getPascal__()) / 100.0
    
    @request("GET", "sensor/pressure/sea/pa")
    @response("%d")
    def getPascalAtSea(self):
        pressure = self.__getPascal__()
        if self.external != None:
            k = self.external.getKelvin()
            if k != 0:
                return float(pressure) / (1.0 / (1.0 + 0.0065 / k * self.altitude)**5.255)
        return float(pressure) / (1.0 - self.altitude / 44330.0)**5.255

    @request("GET", "sensor/pressure/sea/hpa")
    @response("%.2f")
    def getHectoPascalAtSea(self):
        return self.getPascalAtSea() / 100.0
    
class Temperature():
    def __family__(self):
        return "Temperature"
    
    def __getKelvin__(self):
        raise NotImplementedError
    
    def __getCelsius__(self):
        raise NotImplementedError

    def __getFahrenheit__(self):
        raise NotImplementedError
    
    def Kelvin2Celsius(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value - 273.15
    
    def Kelvin2Fahrenheit(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value * 1.8 - 459.67
    
    def Celsius2Kelvin(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value + 273.15
    
    def Celsius2Fahrenheit(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value * 1.8 + 32

    def Fahrenheit2Kelvin(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 459.67) / 1.8

    def Fahrenheit2Celsius(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 32) / 1.8

    @request("GET", "sensor/temperature/k")
    @response("%.02f")
    def getKelvin(self):
        return self.__getKelvin__()
    
    @request("GET", "sensor/temperature/c")
    @response("%.02f")
    def getCelsius(self):
        return self.__getCelsius__()
    
    @request("GET", "sensor/temperature/f")
    @response("%.02f")
    def getFahrenheit(self):
        return self.__getFahrenheit__()
    
class Luminosity():
    def __family__(self):
        return "Luminosity"
    
    def __getLux__(self):
        raise NotImplementedError

    @request("GET", "sensor/luminosity/lux")
    @response("%.02f")
    def getLux(self):
        return self.__getLux__()

class Distance():
    def __family__(self):
        return "Distance"
    
    def __getMillimeter__(self):
        raise NotImplementedError

    @request("GET", "sensor/distance/mm")
    @response("%.02f")
    def getMillimeter(self):
        return self.__getMillimeter__()
    
    @request("GET", "sensor/distance/cm")
    @response("%.02f")
    def getCentimeter(self):
        return self.getMillimeter() / 10
    
    @request("GET", "sensor/distance/m")
    @response("%.02f")
    def getMeter(self):
        return self.getMillimeter() / 1000
    
    @request("GET", "sensor/distance/in")
    @response("%.02f")
    def getInch(self):
        return self.getMillimeter() / 0.254
    
    @request("GET", "sensor/distance/ft")
    @response("%.02f")
    def getFoot(self):
        return self.getInch() / 12
    
    @request("GET", "sensor/distance/yd")
    @response("%.02f")
    def getYard(self):
        return self.getInch() / 36
    
class Humidity():
    def __family__(self):
        return "Humidity"
    
    def __getHumidity__(self):
        raise NotImplementedError    
    
    @request("GET", "sensor/humidity/float")
    @response("%f")
    def getHumidity(self):
        return self.__getHumidity__()
    
    @request("GET", "sensor/humidity/percent")
    @response("%d")
    def getHumidityPercent(self):
        return self.__getHumidity__() * 100
        
DRIVERS = {}
DRIVERS["bmp085"] = ["BMP085", "BMP180"]
DRIVERS["onewiretemp"] = ["DS1822", "DS1825", "DS18B20", "DS18S20", "DS28EA00"]
DRIVERS["tmpXXX"] = ["TMP75", "TMP102", "TMP275"]
DRIVERS["tslXXXX"] = ["TSL2561", "TSL2561CS", "TSL2561T", "TSL4531", "TSL45311", "TSL45313", "TSL45315", "TSL45317"]
DRIVERS["vcnl4000"] = ["VCNL4000"]
DRIVERS["hytXXX"] = ["HYT221"]

