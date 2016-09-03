# Yet Another WebIoPi+
a clone of WebIOPi, the original one is written by Eric PTAK (trouch).
Please refer to http://webiopi.trouch.com/ for the original one.

## WebIOPi-0.7.1 Patch for B+, Pi 2, and Pi 3
Merged a patch for B+, Pi 2, and Pi 3 by Keisuke Seya (doublebind).
Please refer to https://github.com/doublebind/raspi for more details.

# Additional Drivers

Please refer to WebIOPi Device Driver Guide by Andreas Riegg; http://www.t-h-i-n-x.net/resources/WebIOPi-Driver-120.pdf, if you would like to develop a new driver.

## I2C

### BME280 temperature/humidity/pressure sensors
Added Bosch BME280 (temperature, humidity, and pressure) sensors driver written by Evil Asvachin (https://mrevil.asvachin.eu/).
Plase refer to https://groups.google.com/d/msg/webiopi/_m71a-AdF8I/Ju_FJ8s4BQAJ or https://mrevil.asvachin.eu/electronics/weather_station/ for the original resources.

### MCP9808 temperature sensor
Added Microchip MCP9808 high accuracy I2C temperature sensor driver written by Andreas Riegg. Please refer to https://groups.google.com/d/topic/webiopi/Jv4bw9IL-w4/discussion for the original resources.

### MCP3424 ADC driver
Added Microchip MC3424 ADC driver written by Justin Miller. Please refer to https://groups.google.com/d/topic/webiopi/v8xuijB8yyk/discussion for the original resources.

### Analog Devices Digital Potentionmeter 
Added Analog Devices Digital Potentionmeter driver written by Andreas Riegg. Please refer to https://groups.google.com/d/topic/webiopi/8NvzHB-4s98/discussion for the original resources.

* Supported: AD5161I, AD5241, AD5242, AD5243, AD5245, AD5246, AD5247, AD5248, AD5263I, AD5280, AD5282

### PCA953X/PCA9555 IO Expander driver
Added PCA953X series IO Expaner driver written by Andreas Riegg. Plase refer to http://webiopi.trouch.com/issues/122/ for the original resources.

### DS1307 series / MCP7940 RTC driver
Added DS1307, DS1337, DS1338, DS3231 and MCP7940 RTC driver written by Andreas Riegg. Please refer to http://webiopi.trouch.com/issues/116/ for the original resources.

### AT24C compatible 16-bit addressing EEPROM driver 
Added AT24C copatible 16-bit addressing EEPROM driver written by Andreas Riegg. Please refer to http://webiopi.trouch.com/issues/132/ for the original resources.

### HTU21D Temperature/Humidity sensors
Added HTU21D temperature/humidity sensors driver written by Zoltán Zörgő. Please refer to http://webiopi.trouch.com/issues/92/ for original resources.


## SPI

### Analog Devivces Digital Potentionmeter
Added Analog Devices Digital Potentionmeter driver written by Andreas Riegg.

* Supported: AD5160, AD5161S, AD5162, AD5165, AD5200, AD5201, AD5204, AD5206, AD5263S, AD5290, AD8400, AD8402, AD8403

### Analog Devices 5204 family Digital Potentionmeter
Added Analog Devices Digital Potentionmeter driver written by Andreas Riegg.

* Supported: AD5204DC, AD5161DC, AD5263DC, AD5290DC, AD8403DC

# ChangeLog

## master branch
* Added MCP3424 ADC driver by Justin Miller.
* Added I2C/SPI Analog Devices Digital Potentionmeter driver by Andreas Riegg.
* Added I2C MCP9808 temperature sensor written by Andreas Riegg. 
* Updated TSL2561 driver to v1.1 written by Andreas Riegg.
* Added I2C PCA953x series IO Expander driver written by Andreas Riegg.
* Added I2C DS1307 series and MCP7940 RTC driver written by Andreas Riegg.
* Added I2C AT24C compatible 16-bit addressing EEPROM driver written by Andreas Riegg.
* Added I2C HTU21D Temperature/Humidity sensors driver written by Zoltán Zörgő. 

## Version 0.7.1+deb01 (Thu Sep 1 21:37:39 2016 +0900) 
* Merged a patch for B+, Pi 2, and Pi 3 written by Keisuke Seya (doublebind).
* Added Bosch BME280 driver written by Evil Asvachin.
* Added DEBIAN (Raspbian) wheezy and jessie package.
* Supported python2 >= 2.7 and python3 >= 3.2.
* May work on zero.
* Not supported python 2.6.
* Not supported Raspberry Pi Model A and B (26-pin type). 


# Issues

## Closed

* Issue #041 [Accepted/open] - Create debian packages -> Closed by Thor.
* Issue #090 [New/open] - TSL2561 sensor lux value not changing -> Closed by Andreas. 
* Issue #091 [New/open] - New Device: BMP180 -> Closed by Andreas.
* Issue #092 [New/open] - Support for HTU21D -> Closed by Zoltan&Andreas.

## Open

* Issue #040 [Accepted/open] - Improve HTTP request handling
* Issue #042 [Accepted/open] - Improve software PWM to use DMA instead of Threads
* Issue #044 [Accepted/open] - Java (partly Python) client improvement possibilities
* Issue #057 [Accepted/open] - Make macros more RESTful
* Issue #062 [Accepted/open] - Update wiki for missing Serial docs
* Issue #070 [Accepted/open] - Add synchronization/lock to drivers functions call
* Issue #071 [Accepted/open] - Allows Reverse Proxying / custom URL root 
* Issue #074 [Accepted/open] - GPIO Expander Port Write REST Error
* Issue #080 [Accepted/open] - Add Exception handling
* Issue #081 [New/open] - Problems in normal Startup but not in the Debug mode
* Issue #082 [New/open] - Integration of DHT11 Humidity sensors
* Issue #084 [Accepted/open] - Add logout option
* Issue #086 [New/open] - Custard Pi Interface
* Issue #086 [New/open] - Custard Pi Interface
* Issue #087 [New/open] - Some results miss "Content-Type" header
* Issue #089 through #161


