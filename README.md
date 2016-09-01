# Yet Another WebIoPi+
a Clone of WebIOPi, the original one is written by Eric PTAK (trouch).
Please refer to http://webiopi.trouch.com/ for the original one.

## WebIOPi-0.7.1 Patch for B+, Pi 2, and Pi 3
Merged a patch for B+, Pi 2, and Pi 3 by Keisuke Seya (doublebind).
Please refer to https://github.com/doublebind/raspi for more details.

# Additional Drivers

** I2C

### BME280 temperature/humidity/pressure sensors
Added Bosch BME280 (temperature, humidity, and pressure) sensors driver written by Evil Asvachin (https://mrevil.asvachin.eu/).
Plase refer to https://groups.google.com/d/msg/webiopi/_m71a-AdF8I/Ju_FJ8s4BQAJ or https://mrevil.asvachin.eu/electronics/weather_station/ for the original resources.

### MCP9808 temperature sensor
Added Microchip MCP9808 high accuracy I2C temperature sensor driver written by  ndreas Riegg. Please refer to https://groups.google.com/d/topic/webiopi/Jv4bw9IL-w4/discussion for the original resources.


# ChangeLog

## Version 0.7.1+deb01 (Thu Sep 1 21:37:39 2016 +0900) 
* Merged a patch for B+, Pi 2, and Pi 3 written by Keisuke Seya (doublebind).
* Added Bosch BME280 driver written by Evil Asvachin.
* Added DEBIAN (Raspbian) wheezy and jessie package.
* Supported python2 >= 2.7 and python3 >= 3.2.
* May work on zero.
* Not supported python 2.6.
* Not supported Raspberry Pi Model A and B (26-pin type). 




