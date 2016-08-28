#   Copyright 2013 Stuart Marsden
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

from webiopi.devices.onewire import OneWire
from webiopi.devices.digital import GPIOPort

class DS2408(OneWire, GPIOPort):
    FUNCTIONS = [GPIOPort.IN for i in range(8)]

    def __init__(self, slave=None):
        OneWire.__init__(self, slave, 0x29, "2408")
        GPIOPort.__init__(self, 8)
        self.portWrite(0x00)
    
    def __str__(self):
        return "DS2408(slave=%s)" % self.slave
    
    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]
      
    def __setFunction__(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Requested function not supported")
        self.FUNCTIONS[channel] = value
        if value == self.IN:
            self.__output__(channel, 0)

    def __digitalRead__(self, channel):
        mask = 1 << channel
        d = self.readState()
        if d != None:
            return (d & mask) == mask

        
    def __digitalWrite__(self, channel, value):
        mask = 1 << channel
        b = self.readByte()
        if value:
            b |= mask
        else:
            b &= ~mask
        self.writeByte(b)
        
    def __portWrite__(self, value):
        self.writeByte(value)
        
    def __portRead__(self):
        return self.readByte()
        
    def readState(self):
        try:
            with open("/sys/bus/w1/devices/%s/state" % self.slave, "rb") as f:
                data = f.read(1)
            return ord(data)
        except IOError:
            return -1

    def readByte(self):
        try:
            with open("/sys/bus/w1/devices/%s/output" % self.slave, "rb") as f:
                data = f.read(1)
            return bytearray(data)[0]
        except IOError:
            return -1
      
    def writeByte(self, value):
        try:
            with open("/sys/bus/w1/devices/%s/output" % self.slave, "wb") as f:
                f.write(bytearray([value]))
        except IOError:
                pass
            
        
