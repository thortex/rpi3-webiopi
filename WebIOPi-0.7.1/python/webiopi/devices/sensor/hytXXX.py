#   Copyright 2014 Michael Burget, Eric PTAK
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

from time import sleep
from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Temperature,Humidity

class HYT221(I2C, Temperature, Humidity):
    VAL_RETRIES = 30
    
    def __init__(self, slave=0x28):
        I2C.__init__(self, toint(slave))
        self.__startMeasuring__()
        
    def __str__(self):
        return "HYT221(slave=0x%02X)" % self.slave
            
    def __family__(self):
        return [Temperature.__family__(self), Humidity.__family__(self)]
    
    def __startMeasuring__(self):
      self.writeByte(0x0)
      
    def readRawData(self):
        self.__startMeasuring__()
        for i in range(self.VAL_RETRIES):
            #C-code example from sensor manufacturer suggest to wait 100ms (Duration of the measurement)
            # no to get the very last measurement shoudn't be a problem -> wait 10ms
            # try a read every 10 ms for maximum VAL_RETRIES times
            sleep(.01)
            data_bytes=self.readBytes(4)
            stale_bit = (data_bytes[0] & 0b01000000) >> 6
            if (stale_bit == 0):    
                raw_t = ((data_bytes[2] << 8) | data_bytes[3]) >> 2
                raw_h = ((data_bytes[0] & 0b00111111) << 8) | data_bytes[1]
                return (raw_t, raw_h)

        #Stale was never 0, so datas are not actual
        raise Exception("HYT221(slave=0x%02X): data fetch timeout" % self.slave)
            
    
    def __getCelsius__(self):
        (raw_t, raw_h) = self.readRawData()
        if raw_t < 0x3FFF:
            return (raw_t * 165.0 / 2**14) - 40.0
        else:
            raise ValueError("Temperature value out of range (RawValue=0x%04X Max:0x3FFF)" % raw_t)
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getHumidity__(self):
        (raw_t, raw_h) = self.readRawData()
        if raw_h < 0x3FFF:
            return raw_h * 1.0 / 2**14
        else:
            raise ValueError("Humidity value out of range (RawValue=0x%04X Max:0x3FFF)" % raw_h)
       
