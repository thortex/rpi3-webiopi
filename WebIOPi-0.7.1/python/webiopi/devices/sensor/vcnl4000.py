#   Copyright 2013 Andreas Riegg
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
#
#   Changelog
#
#   1.0    2013/02/24    Initial release. Luminosity is final. Proximity is good beta
#                        and a working coarse estimation for distance value.
#                        

import time
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Luminosity, Distance
from webiopi.utils.types import toint
from webiopi.utils.logger import debug 

class VCNL4000(I2C, Luminosity, Distance):
    REG_COMMAND           = 0x80
    REG_IR_LED_CURRENT    = 0x83
    REG_AMB_PARAMETERS    = 0x84
    REG_AMB_RESULT_HIGH   = 0x85
    REG_PROX_RESULT_HIGH  = 0x87
    REG_PROX_FREQUENCY    = 0x89
    REG_PROX_ADJUST       = 0x8A
   
    VAL_MOD_TIMING_DEF    = 129 # default from data sheet
    
    VAL_PR_FREQ_3M125HZ   = 0
    VAL_PR_FREQ_1M5625HZ  = 1
    VAL_PR_FREQ_781K25HZ  = 2
    VAL_PR_FREQ_390K625HZ = 3
    
    VAL_START_AMB         = 1 << 4
    VAL_START_PROX        = 1 << 3
    
    VAL_INVALID           = -1
    VAL_NO_PROXIMITY      = -1
    
    MASK_PROX_FREQUENCY  = 0b00111111
    MASK_IR_LED_CURRENT  = 0b00111111
    MASK_PROX_READY      = 0b00100000
    MASK_AMB_READY       = 0b01000000
    
    def __init__(self, slave=0b0010011, current=20, frequency=781, prox_threshold=15, prox_cycles=10, cal_cycles= 5):
        I2C.__init__(self, toint(slave))
        self.setCurrent(toint(current))
        self.setFrequency(toint(frequency))
        self.prox_threshold = toint(prox_threshold)
        self.prox_cycles = toint(prox_cycles)
        self.cal_cycles = toint(cal_cycles)
        self.__setProximityTiming__()
        self.__setAmbientMeasuringMode__()
        time.sleep(0.001)
        self.calibrate() # may have to be repeated from time to time or before every proximity measurement

    def __str__(self):
        return "VCNL4000(slave=0x%02X)" % self.slave

    def __family__(self):
        return [Luminosity.__family__(self), Distance.__family__(self)]

    def __setProximityTiming__(self):
        self.writeRegister(self.REG_PROX_ADJUST, self.VAL_MOD_TIMING_DEF)
                               
    def __setAmbientMeasuringMode__(self):
        ambient_parameter_bytes = 1 << 7 | 1 << 3 | 5
        # Parameter is set to
        # -continuous conversion mode (bit 7)
        # -auto offset compensation (bit 3)
        # -averaging 32 samples (5)
        self.writeRegister(self.REG_AMB_PARAMETERS, ambient_parameter_bytes)

    def calibrate(self):
        self.offset = self.__measureOffset__()
        debug ("VCNL4000: offset = %d" % (self.offset))
        return self.offset

        
    def setCurrent(self, current):
        self.current = current
        self.__setCurrent__()
        

    def getCurrent(self):
        return self.__getCurrent__()

    def setFrequency(self, frequency):
        self.frequency = frequency
        self.__setFrequency__()

    def getFrequency(self):
        return self.__getFrequency__()

    def __setFrequency__(self):
        if not self.frequency in [391, 781, 1563, 3125]:
            raise ValueError("Frequency %d out of range [%d,%d,%d,,%d]" % (self.frequency, 391, 781, 1563, 3125))
        if self.frequency == 391:
            bits_frequency = self.VAL_PR_FREQ_390K625HZ
        elif self.frequency == 781:
            bits_frequency = self.VAL_PR_FREQ_781K25HZ
        elif self.frequency == 1563:
            bits_frequency = self.VAL_PR_FREQ_1M5625HZ            
        elif self.frequency == 3125:
            bits_frequency = self.VAL_PR_FREQ_3M125HZ
        self.writeRegister(self.REG_PROX_FREQUENCY, bits_frequency)
        debug ("VCNL4000: new freq = %d" % (self.readRegister(self.REG_PROX_FREQUENCY)))
        
    def __getFrequency__(self):
        bits_frequency = self.readRegister(self.REG_PROX_FREQUENCY) & self.MASK_PROX_FREQUENCY
        if bits_frequency == self.VAL_PR_FREQ_390K625HZ:
            f =  391
        elif bits_frequency == self.VAL_PR_FREQ_781K25HZ:
            f =  781
        elif bits_frequency == self.VAL_PR_FREQ_1M5625HZ:
            f = 1563
        elif bits_frequency == self.VAL_PR_FREQ_3M125HZ:
            f = 3125
        else:
            f = self.VAL_INVALID # indicates undefined
        return f

    def __setCurrent__(self):
        if not self.current in range(0,201):
            raise ValueError("%d mA LED current out of range [%d..%d] mA" % (self.current, 0, 201))
        self.writeRegister(self.REG_IR_LED_CURRENT, int(self.current / 10))       
        debug ("VCNL4000: new curr = %d" % (self.readRegister(self.REG_IR_LED_CURRENT)))
        
    def __getCurrent__(self):
        bits_current = self.readRegister(self.REG_IR_LED_CURRENT) & self.MASK_IR_LED_CURRENT
        return bits_current * 10
        
    def __getLux__(self):
        self.writeRegister(self.REG_COMMAND, self.VAL_START_AMB)
        while not (self.readRegister(self.REG_COMMAND) & self.MASK_AMB_READY):
            time.sleep(0.001)
        light_bytes = self.readRegisters(self.REG_AMB_RESULT_HIGH, 2)
        light_word = light_bytes[0] << 8 | light_bytes[1]
        return self.__calculateLux__(light_word)
         
    def __calculateLux__(self, light_word):
        return (light_word + 3) * 0.25 # From VISHAY application note

    def __getMillimeter__(self):
        success = 0
        fail = 0
        prox = 0
        match_cycles = self.prox_cycles
        while (fail < match_cycles) & (success < match_cycles):
            real_counts = self.__readProximityCounts__() - self.offset 
            if real_counts > self.prox_threshold:
                success += 1
                prox += real_counts
            else:
                fail += 1
        if fail == match_cycles:
            return self.VAL_NO_PROXIMITY
        else:
            return self.__calculateMillimeter__(prox // match_cycles)
    
    def __calculateMillimeter__(self, raw_proximity_counts):
        # According to chip spec the proximity counts are strong non-linear with distance and cannot be calculated
        # with a direct formula. From experience found on web this chip is generally not suited for really exact
        # distance calculations. This is a rough distance estimation lookup table for now. Maybe someone can
        # provide a more exact approximation in the future.

        debug ("VCNL4000: prox real raw counts = %d" % (raw_proximity_counts))
        if raw_proximity_counts >= 10000:
            estimated_distance = 0
        elif raw_proximity_counts >= 3000:
            estimated_distance = 5
        elif raw_proximity_counts >= 900:
            estimated_distance = 10
        elif raw_proximity_counts >= 300:
            estimated_distance = 20
        elif raw_proximity_counts >= 150:
            estimated_distance = 30
        elif raw_proximity_counts >= 75:
            estimated_distance = 40
        elif raw_proximity_counts >= 50:
            estimated_distance = 50
        elif raw_proximity_counts >= 25:
            estimated_distance = 70
        else:
            estimated_distance = 100
        return estimated_distance
    
    def __measureOffset__(self):
        offset = 0
        for unused in range(self.cal_cycles):
            offset += self.__readProximityCounts__()
        return offset // self.cal_cycles
        
    def __readProximityCounts__(self):
        self.writeRegister(self.REG_COMMAND, self.VAL_START_PROX)
        while not (self.readRegister(self.REG_COMMAND) & self.MASK_PROX_READY):
            time.sleep(0.001)
        proximity_bytes = self.readRegisters(self.REG_PROX_RESULT_HIGH, 2)
        debug ("VCNL4000: prox raw value = %d" % (proximity_bytes[0] << 8 | proximity_bytes[1]))
        return (proximity_bytes[0] << 8 | proximity_bytes[1])
    