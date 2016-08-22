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

import sys
from webiopi.devices.onewire import OneWire
from webiopi.devices.sensor import Temperature

class OneWireTemp(OneWire, Temperature):
    def __init__(self, slave=None, family=0, name="1-Wire"):
        OneWire.__init__(self, slave, family, "TEMP")
        self.name = name
        
    def __str__(self):
        return "%s(slave=%s)" % (self.name, self.slave)
    
    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        data = self.read()
        lines = data.split("\n")
        if lines[0].endswith("YES"):
            i = lines[1].find("=")
            temp = lines[1][i+1:]
            return int(temp) / 1000.0
        return (-sys.maxsize - 1) / 1000.0
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class DS18S20(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x10, "DS18S20")
        
class DS1822(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x22, "DS1822")
        
class DS18B20(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x28, "DS18B20")
        
class DS1825(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x3B, "DS1825")
        
class DS28EA00(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x42, "DS28EA00")
