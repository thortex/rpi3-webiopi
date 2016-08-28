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

import os
import time
import subprocess

from webiopi.utils.logger import debug, info

BUSLIST = {
    "I2C": {"enabled": False, "gpio": {0:"SDA", 1:"SCL", 2:"SDA", 3:"SCL"}, "modules": ["i2c-bcm2708", "i2c-dev"]},
    "SPI": {"enabled": False, "gpio": {7:"CE1", 8:"CE0", 9:"MISO", 10:"MOSI", 11:"SCLK"}, "modules": ["spi-bcm2708", "spidev"]},
    "UART": {"enabled": False, "gpio": {14:"TX", 15:"RX"}},
    "ONEWIRE": {"enabled": False, "gpio": {4:"DATA"}, "modules": ["w1-gpio"], "wait": 2}
}

def loadModule(module):
    debug("Loading module : %s" % module)
    subprocess.call(["modprobe", module])
    
def unloadModule(module):
    subprocess.call(["modprobe", "-r", module])
    
def loadModules(bus):
    if BUSLIST[bus]["enabled"] == False and not modulesLoaded(bus):
        info("Loading %s modules" % bus)
        for module in BUSLIST[bus]["modules"]:
            loadModule(module)
        if "wait" in BUSLIST[bus]:
            info("Sleeping %ds to let %s modules load" % (BUSLIST[bus]["wait"], bus))
            time.sleep(BUSLIST[bus]["wait"])

    BUSLIST[bus]["enabled"] = True

def unloadModules(bus):
    info("Unloading %s modules" % bus)
    for module in BUSLIST[bus]["modules"]:
        unloadModule(module)
    BUSLIST[bus]["enabled"] = False
        
def __modulesLoaded__(modules, lines):
    if len(modules) == 0:
        return True
    for line in lines:
        if modules[0].replace("-", "_") == line.split(" ")[0]:
            return __modulesLoaded__(modules[1:], lines)
    return False

def modulesLoaded(bus):
    if not bus in BUSLIST or not "modules" in BUSLIST[bus]:
        return True

    try:
        with open("/proc/modules") as f:
            c = f.read()
            f.close()
            lines = c.split("\n")
            return __modulesLoaded__(BUSLIST[bus]["modules"], lines)
    except:
        return False

def checkAllBus():
    for bus in BUSLIST:
        if modulesLoaded(bus):
            BUSLIST[bus]["enabled"] = True

class Bus():
    def __init__(self, busName, device, flag=os.O_RDWR):
        loadModules(busName)
        self.busName = busName
        self.device = device
        self.flag = flag
        self.fd = 0
        self.open()
        
    def open(self):
        self.fd = os.open(self.device, self.flag)
        if self.fd < 0:
            raise Exception("Cannot open %s" % self.device)

    def close(self):
        if self.fd > 0:
            os.close(self.fd)
    
    def read(self, size=1):
        if self.fd > 0:
            return os.read(self.fd, size)
        raise Exception("Device %s not open" % self.device)
    
    def readBytes(self, size=1):
        return bytearray(self.read(size))
    
    def readByte(self):
        return self.readBytes()[0]

    def write(self, string):
        if self.fd > 0:
            return os.write(self.fd, string)
        raise Exception("Device %s not open" % self.device)
    
    def writeBytes(self, data):
        return self.write(bytearray(data))

    def writeByte(self, value):
        self.writeBytes([value])
        
