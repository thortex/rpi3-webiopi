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

import fcntl

from webiopi.utils.version import BOARD_REVISION
from webiopi.devices.bus import Bus

# /dev/i2c-X ioctl commands.  The ioctl's parameter is always an
# unsigned long, except for:
#    - I2C_FUNCS, takes pointer to an unsigned long
#    - I2C_RDWR, takes pointer to struct i2c_rdwr_ioctl_data
#    - I2C_SMBUS, takes pointer to struct i2c_smbus_ioctl_data

I2C_RETRIES = 0x0701    # number of times a device address should
                        # be polled when not acknowledging
I2C_TIMEOUT = 0x0702    # set timeout in units of 10 ms

# NOTE: Slave address is 7 or 10 bits, but 10-bit addresses
# are NOT supported! (due to code brokenness)

I2C_SLAVE       = 0x0703    # Use this slave address
I2C_SLAVE_FORCE = 0x0706    # Use this slave address, even if it
                            # is already in use by a driver!
I2C_TENBIT      = 0x0704    # 0 for 7 bit addrs, != 0 for 10 bit

I2C_FUNCS       = 0x0705    # Get the adapter functionality mask

I2C_RDWR        = 0x0707    # Combined R/W transfer (one STOP only)

I2C_PEC         = 0x0708    # != 0 to use PEC with SMBus
I2C_SMBUS       = 0x0720    # SMBus transfer */


class I2C(Bus):
    def __init__(self, slave):
        self.channel = 0
        if BOARD_REVISION > 1:
            self.channel = 1

        Bus.__init__(self, "I2C", "/dev/i2c-%d" % self.channel)
        self.slave = slave
        if fcntl.ioctl(self.fd, I2C_SLAVE, self.slave):
            raise Exception("Error binding I2C slave 0x%02X" % self.slave)
        
    def __str__(self):
        return "I2C(slave=0x%02X)" % self.slave
    
    def readRegister(self, addr):
        self.writeByte(addr)
        return self.readByte()
    
    def readRegisters(self, addr, count):
        self.writeByte(addr)
        return self.readBytes(count)
    
    def writeRegister(self, addr, byte):
        self.writeBytes([addr, byte])
    
    def writeRegisters(self, addr, buff):
        d = bytearray(len(buff)+1)
        d[0] = addr
        d[1:] = buff
        self.writeBytes(d)
