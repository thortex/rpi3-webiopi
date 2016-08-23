from webiopi.utils.types import toint, signInteger
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Temperature, Pressure, Humidity
from webiopi.utils import logger

class BME280(I2C, Temperature, Pressure, Humidity):
    def __init__(self, altitude=0, external=None, oversampling=0, filter=0, standby=0.5, slave=0x76):
        I2C.__init__(self, toint(slave))
        Pressure.__init__(self, altitude, external)

        self.t1 = self.readUnsigned(0x88, 2)
        self.t2 = self.readSigned(0x8A, 2)
        self.t3 = self.readSigned(0x8C, 2)

        self.p1 = self.readUnsigned(0x8E, 2)
        self.p2 = self.readSigned(0x90, 2)
        self.p3 = self.readSigned(0x92, 2)
        self.p4 = self.readSigned(0x94, 2)
        self.p5 = self.readSigned(0x96, 2)
        self.p6 = self.readSigned(0x98, 2)
        self.p7 = self.readSigned(0x9A, 2)
        self.p8 = self.readSigned(0x9C, 2)
        self.p9 = self.readSigned(0x9E, 2)

        self.h1 = self.readUnsigned(0xA1, 1)
        self.h2 = self.readSigned(0xE1, 2)
        self.h3 = self.readUnsigned(0xE3, 1)
        self.h4 = (self.readUnsigned(0xE4, 1) << 4) | (self.readUnsigned(0xE5, 1) & 0x0F)
        self.h5 = (self.readSigned(0xE6, 1) << 4) | (self.readSigned(0xE5, 1) >> 4)
        self.h6 = self.readSigned(0xE7, 1)

        oversamplingBits = toint(oversampling).bit_length()
        self.writeRegister(0xF2, oversamplingBits) # Humidity oversampling. Must be set before temp/press oversampling (see datasheet 5.4.3).
        self.writeRegister(0xF4, (oversamplingBits << 5) | (oversamplingBits << 2) | 0x03) # Pressure, temperature oversampling, sensor normal mode.

        standbyValues = {'0.5':0, '10':6, '20':7, '62.5':1, '125':2, '250':3, '500':4, '1000':5}
        if standby in standbyValues:
            tStandbyBits = standbyValues[standby]
        else:
            tStandbyBits = 0 # Default to 0.5ms t_standby
            logger.warn('Invalid value for standby: %s' % standby)
        spiBits = 0 # No SPI of course.
        filterBits = toint(filter) >> 1
        self.writeRegister(0xF5, (tStandbyBits << 5) | (filterBits << 2) | spiBits)

    def __str__(self):
        return "BME280"

    def __family__(self):
        return [Temperature.__family__(self), Pressure.__family__(self), Humidity.__family__(self)]

    def readUnsigned(self, address, numBytes, byteOrder='little'):
        d = self.readRegisters(address, numBytes)
        x = 0
        if byteOrder == 'big':
            for i in range(0, numBytes):
                x |= d[i] << (8 * (numBytes - (i + 1)))
        else:
            for i in range(0, numBytes):
                x |= d[i] << (8 * i)
        return x

    def readSigned(self, address, numBytes, byteOrder = 'little'):
        d = self.readUnsigned(address, numBytes, byteOrder)
        return signInteger(d, numBytes * 8)

    # Reading all ADC registers at once ensures consistency (see datasheet section 4).
    def readAdc(self):
        raw = self.readUnsigned(0xF7, 8, 'big')
        adc_P = raw >> 44
        adc_T = ((raw >> 16) & 0xFFFFFF) >> 4
        adc_H = raw & 0xFFFF
        return (adc_T, adc_P, adc_H)

    def compensateTfine(self, adc_T):
        #Taken straight out of the datasheet. Could be rewritten to be clearer.
        var1 = (((adc_T >> 3) - (self.t1 << 1)) * self.t2) >> 11
        var2 = (((((adc_T >> 4) - self.t1) * ((adc_T >> 4) - self.t1)) >> 12) * self.t3) >> 14

        return var1 + var2

    def compensateT(self, t_fine):
        #Taken straight out of the datasheet. Could be rewritten to be clearer.
        return float((t_fine * 5 + 128) >> 8) / 100.0

    def compensateP(self, t_fine, adc_P):
        #Taken straight out of the datasheet. Could be rewritten to be clearer.
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.p6
        var2 = var2 + ((var1 * self.p5) << 17)
        var2 = var2 + (self.p4 << 35)
        var1 = ((var1 * var1 * self.p3) >> 8) + ((var1 * self.p2) << 12)
        var1 = ((1 << 47) + var1) * self.p1 >> 33

        if var1 == 0:
            return 0

        p = 1048576 - adc_P
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.p9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.p8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.p7 << 4)

        return float(p) / 256.0

    def compensateH(self, t_fine, adc_H):
        #Taken straight out of the datasheet. Could be rewritten to be clearer.
        v_x1_u32r = t_fine - 76800
        v_x1_u32r = ((((adc_H << 14) - (self.h4 << 20) - (self.h5 * v_x1_u32r)) + 16384) >> 15) * (((((((v_x1_u32r * self.h6) >> 10) * (((v_x1_u32r * self.h3) >> 11) + 32768)) >> 10) + 2097152) * self.h2 + 8192) >> 14)
        v_x1_u32r = v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * self.h1) >> 4)
        v_x1_u32r = max(v_x1_u32r, 0)
        v_x1_u32r = min(v_x1_u32r, 419430400)

        return float(v_x1_u32r >> 12) / 1024.0

    def __getAll__(self):
        raw = self.readUnsigned(0xF7, 8, 'big')
        adc_P = raw >> 44
        adc_T = ((raw >> 16) & 0xFFFFFF) >> 4
        adc_H = raw & 0xFFFF
        t_fine = self.compensateTfine(adc_T)
        T = self.compensateT(t_fine)
        P = self.compensateP(t_fine, adc_P)
        H = self.compensateH(t_fine, adc_H)
        return (T, P, H)

    def __getCelsius__(self):
        adc = self.readAdc()
        t_fine = self.compensateTfine(adc.T)
        return self.compensateT(t_fine)

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

    def __getPascal__(self):
        adc = self.readAdc()
        t_fine = self.compensateTfine(adc.T)
        return self.compensateP(t_fine, adc.P)

    def __getHumidity__(self):
        adc = self.readAdc()
        t_fine = self.compensateTfine(adc.T)
        return self.compensateH(t_fine, adc.H) / 100.0
