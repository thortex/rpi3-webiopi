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
from webiopi.devices.bus import Bus, loadModule

EXTRAS = {
    "TEMP": {"loaded": False, "module": "w1-therm"},
    "2408": {"loaded": False, "module": "w1_ds2408"}

}

def loadExtraModule(name):
    if EXTRAS[name]["loaded"] == False:
        loadModule(EXTRAS[name]["module"])
        EXTRAS[name]["loaded"] = True

class OneWire(Bus):
    def __init__(self, slave=None, family=0, extra=None):
        Bus.__init__(self, "ONEWIRE", "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves", os.O_RDONLY)
        if self.fd > 0:
            os.close(self.fd)
            self.fd = 0

        self.family = family
        if  slave != None:
            addr = slave.split("-")
            if len(addr) == 1:
                self.slave = "%02x-%s" % (family, slave)
            elif len(addr) == 2:
                prefix = int(addr[0], 16)
                if family > 0 and family != prefix:
                    raise Exception("1-Wire slave address %s does not match family %02x" % (slave, family))
                self.slave = slave
        else:
            devices = self.deviceList()
            if len(devices) == 0:
                raise Exception("No device match family %02x" % family)
            self.slave = devices[0]

        loadExtraModule(extra)
        
    def __str__(self):
        return "1-Wire(slave=%s)" % self.slave
    
    def deviceList(self):
        devices = []
        with open(self.device) as f:
            lines = f.read().split("\n")
            if self.family > 0:
                prefix = "%02x-" % self.family
                for line in lines:
                    if line.startswith(prefix):
                        devices.append(line)
            else:
                devices = lines
        return devices;
    
    def read(self):
        with open("/sys/bus/w1/devices/%s/w1_slave" % self.slave) as f:
            data = f.read()
        return data

