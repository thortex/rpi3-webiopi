#   Copyright 2014 Zoltán Zörgő <soltan.zorgo@gmail.com>
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
#   Sensor datasheet: http://www.meas-spec.com/downloads/HTU21D.pdf
#   
#   Credits to: Jay Wineinger <jay.wineinger@gmail.com>
#   Based on: https://github.com/jwineinger/quick2wire-HTU21D/blob/master/htu21d.py

import time
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Temperature,Humidity
from webiopi.utils.types import toint

class CRCFailed(Exception): pass

class HTU21D(I2C, Temperature, Humidity):

    CMD_READ_TEMP_HOLD = 0xe3
    CMD_READ_HUM_HOLD = 0xe5
    CMD_READ_TEMP_NOHOLD = 0xf3
    CMD_READ_HUM_NOHOLD = 0xf5
    CMD_WRITE_USER_REG = 0xe6
    CMD_READ_USER_REG = 0xe7
    CMD_SOFT_RESET= 0xfe

    # uses bits 7 and 0 of the user_register mapping
    # to the bit resolutions of (relative humidity, temperature)
    RESOLUTIONS = {
        (0, 0) : (12, 14),
        (0, 1) : (8, 12),
        (1, 0) : (10, 13),
        (1, 1) : (11, 11),
    }

    # sets up the times to wait for measurements to be completed. uses the
    # max times from the datasheet plus a healthy safety margin (10-20%)
    MEASURE_TIMES = {
        (12, 14): (.018, .055),
        (8, 12): (.005, .015),
        (10, 13): (.006, .028),
        (11, 11): (.01, .009),
    }

    def __init__(self):
        I2C.__init__(self, 0x40)
        
        self.resolutions = self.get_resolutions()
        self.rh_timing, self.temp_timing = self.MEASURE_TIMES[self.resolutions]
        
    def __str__(self):
        return "HTU21D(slave=0x%02X)" % self.slave
    
    def __family__(self):
        return [Temperature.__family__(self), Humidity.__family__(self)]
        
    def check_crc(self, sensor_val):
        message_from_sensor = sensor_val >> 8
        check_value_from_sensor = sensor_val & 0x0000FF

        remainder = message_from_sensor << 8 # Pad with 8 bits because we have to add in the check value
        remainder |= check_value_from_sensor # Add on the check value

        divisor = 0x988000 # This is the 0x0131 polynomial shifted to farthest left of three bytes

        # Operate on only 16 positions of max 24. The remaining 8 are our remainder and should be zero when we're done.
        for i in range(16):

            if remainder & (1<<(23 - i)):  #Check if there is a one in the left position
              remainder ^= divisor

            divisor >>= 1 # Rotate the divisor max 16 times so that we have 8 bits left of a remainder

        if remainder:
            raise CRCFailed("CRC checksum failed.")

    def reset(self):
        self.writeByte(self.CMD_SOFT_RESET);
        time.sleep(.02)

    def set_resolution(self, resIndex):
        self.writeRegister(self.CMD_WRITE_USER_REG, resIndex)
        time.sleep(.02)
    
    def get_resolutions(self):
        user_reg = self.readRegister(self.CMD_READ_USER_REG)
        return self.RESOLUTIONS[user_reg >> 6, user_reg & 0x1]
        
    def get_temp(self):
        self.writeByte(self.CMD_READ_TEMP_NOHOLD);
        time.sleep(self.temp_timing)
        results = self.readBytes(3)
        raw_temp = int.from_bytes(results, byteorder="big")
        self.check_crc(raw_temp)
        
        results[1] = results[1] & 0xFC # clear status bits
        raw_temp = int.from_bytes(results, byteorder="big")
        return -46.85 + (175.72 * ((raw_temp >> 8) / float(2**16)))

    def get_rel_humidity(self):
        self.writeByte(self.CMD_READ_HUM_NOHOLD);
        time.sleep(self.rh_timing)
        results = self.readBytes(3)        
        raw_hum = int.from_bytes(results, byteorder="big")
        self.check_crc(raw_hum)
        
        results[1] = results[1] & 0xFC # clear status bits
        raw_hum = int.from_bytes(results, byteorder="big")
        return -6 + (125 * ((raw_hum >> 8) / float(2**16)))
    
    def get_comp_rel_humidity(self):
        RHactualT = self.get_rel_humidity()
        Tactual = self.get_temp()
        CoeffTemp = -0.15 # from datasheet
        return RHactualT + (25 - Tactual)*CoeffTemp
    
    def __getCelsius__(self):
        self.reset()
        return self.get_temp()
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

    def __getKelvin__(self):
        return self.Celsius2Kelvin()
    
    def __getHumidity__(self):
        self.reset()
        return self.get_comp_rel_humidity() / 100.00
