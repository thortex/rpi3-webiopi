#!/usr/bin/python3
#   MCP3424 driver written for webopi
#	written by Justin Miller
#	example by ABElectronics, ABE_ADCPi.py used as a template.
#	tested on the ADCPi (qty2)
"""
Device notes
* When you read from the device over I2C, the device returns the data bytes 
  followed by the configuration byte.
* 18 bit resolution - 3 data bytes, followed by the config byte.
* 12 to 16 bit resolution, 2 data bytes, followed by the config byte.
* unused bits to the left of the MSB mirror the MSB(sign bit) and can be ignored.
* twos compliment is used for negative values. (not implemented here)
* 18 bit format byte_1(6 bits to ignore, 1 sign bit, 1 data bit) byte_2(8 data bits) 
  byte_3(8 data bits) byte_4(config byte)
* 16 bit format byte_1(1 sign bit, 7 data bits) byte_2(8 data bits) byte_3(config byte)
* 14 bit format byte_1(2 bits to ignore, 1 sign bit, 5 data bits), byte_2(8 data bits), 
  byte_3(config byte)
* 12 bit format byte_1(4 bits to ignore, 1 sign bit, 3 data bits), byte_2(8 data bits), 
  byte_3(config byte)
 
* Since this chip reads +/- voltage, the MSB is actually a sign bit.  This breaks the 
  -analogMax calculation in /devices/analog/__init__.py.  To fix it, send (resolution-1)
  rather than resolution to __init__.py { so that max = 2**(resolution-1)-1 }
  
  /etc/webiopi/config notes:
  example config to be placed in [DEVICES]
  mcp1 = MCP3424 slave:0x68 resolution:12 name:ADC1 gain:1   
  mcp2 = MCP3424 slave:0x69 resolution:16 name:ADC2 gain:1  

  In webiopi/devices/analog/__init__.py
  Add the following line
  DRIVERS["mcp3424"] = ["MCP3424"]
"""


from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.analog import ADC


class MCP3424(ADC, I2C):
    # internal variables
	__address = 0x68  # default address for adc 1 on ADCPi and delta-sigma pi
	__channel = 0  # current channel 
	__config = 0x10  # PGAx1, 12 bit, one-shot conversion, channel 1 (0001 0000)

    # create byte array and fill with initial values to define size
	__adcreading = bytearray()
	__adcreading.append(0x00)
	__adcreading.append(0x00)
	__adcreading.append(0x00)
	__adcreading.append(0x00)

    # local methods
	def __str__(self):
		return "MCP3424(slave=0x%02X)" % self.__address	

	def __updatebyte(self, byte, bit, value):
        # internal method for setting the value of a single bit within a byte
		# send the byte to modify, which bit, and the value to set it to.
		if value == 0:
			return byte & ~(1 << bit)
		elif value == 1:
			return byte | (1 << bit)

	def __checkbit(self, byte, bit):
        # internal method for reading the value of a single bit within a byte
		bitval = ((byte & (1 << bit)) != 0)
		if (bitval == 1):
			return True
		else:
			return False

	def __setchannel(self, channel):
        # internal method for updating the config to the selected channel
		if channel != self.__channel:
			if channel == 0:
				self.__config = self.__updatebyte(self.__config, 5, 0)
				self.__config = self.__updatebyte(self.__config, 6, 0)
				self.__channel = 0
			if channel == 1:
				self.__config = self.__updatebyte(self.__config, 5, 1)
				self.__config = self.__updatebyte(self.__config, 6, 0)
				self.__channel = 1
			if channel == 2:
				self.__config = self.__updatebyte(self.__config, 5, 0)
				self.__config = self.__updatebyte(self.__config, 6, 1)
				self.__channel = 2
			if channel == 3:
				self.__config = self.__updatebyte(self.__config, 5, 1)
				self.__config = self.__updatebyte(self.__config, 6, 1)
				self.__channel = 3
		return

    # init object with i2c address, default is 0x68, 0x69 for ADCoPi board
	def __init__(self, slave, resolution, name, gain=1):

		self.__address = toint(slave)
		self.resolution = toint(resolution)
		self.initResolution = toint(resolution)-1
		self.name = name
		self.gain = toint(gain)
		self.channelCount = 4
		self.byteCount = 3	
		#pass the integer of the chip address to I2C.__init__
		I2C.__init__(self, self.__address) 
		#pass the ADC channel, resolution, and vref to ADC.__init__
		ADC.__init__(self, self.channelCount, self.initResolution, vref=5)  
		#setBitRate and set_pga must follow I2C and ADC init()
		#The I2C bus must be set up first.
		self.setBitRate(self.resolution)
		self.set_pga(self.gain)	# set the gain	

	def __analogRead__(self, channel, diff=False):
		# reads the raw value from the selected adc channel - channels 0 to 3
		h = 0
		l = 0
		m = 0
		s = 0

		if self.resolution == 18: #set the number of bytes for 1 sample
			self.byteCount = 4
		else:
			self.byteCount = 3
			
		self.__setchannel(channel) #set the config bits for the desired channel.
		
        # keep reading the adc data until the conversion result is ready
		while True:
			__adcreading = self.readRegisters(self.__config, self.byteCount)
			if self.resolution == 18:
				h = __adcreading[0]
				m = __adcreading[1]
				l = __adcreading[2]
				s = __adcreading[3]
			else:
				h = __adcreading[0]
				m = __adcreading[1]
				s = __adcreading[2]       
			if self.__checkbit(s, 7) == 0:
				break

		self.__signbit = False
		t = 0.0
		
        # extract the returned bytes and combine in the correct order 
		if self.resolution == 18:
			t = ((h & 0b00000011) << 16) | (m << 8) | l
			self.__signbit = bool(self.__checkbit(t, 17))
			if self.__signbit:
				t = self.__updatebyte(t, 17, 0)

		if self.resolution == 16:
			t = (h << 8) | m
			self.__signbit = bool(self.__checkbit(t, 15))
			if self.__signbit:
				t = self.__updatebyte(t, 15, 0)

		if self.resolution == 14:
			t = ((h & 0b00111111) << 8) | m
			self.__signbit = self.__checkbit(t, 13)
			if self.__signbit:
				t = self.__updatebyte(t, 13, 0)

		if self.resolution == 12:
			t = ((h & 0b00001111) << 8) | m		
			self.__signbit = self.__checkbit(t, 11)
			if self.__signbit:
				t = self.__updatebyte(t, 11, 0)

		return t

	def set_pga(self, gain): #set the gain bits in __config

		if gain == 1:
			self.__config = self.__updatebyte(self.__config, 0, 0)
			self.__config = self.__updatebyte(self.__config, 1, 0)
		if gain == 2:
			self.__config = self.__updatebyte(self.__config, 0, 1)
			self.__config = self.__updatebyte(self.__config, 1, 0)
		if gain == 4:
			self.__config = self.__updatebyte(self.__config, 0, 0)
			self.__config = self.__updatebyte(self.__config, 1, 1)
		if gain == 8:
			self.__config = self.__updatebyte(self.__config, 0, 1)
			self.__config = self.__updatebyte(self.__config, 1, 1)

		self.writeRegister(self.__address, self.__config)	
		return

	def setBitRate(self, rate): #set the resolution bits in __config

		if rate == 12:
			self.__config = self.__updatebyte(self.__config, 2, 0)
			self.__config = self.__updatebyte(self.__config, 3, 0)
		if rate == 14:
			self.__config = self.__updatebyte(self.__config, 2, 1)
			self.__config = self.__updatebyte(self.__config, 3, 0)
		if rate == 16:
			self.__config = self.__updatebyte(self.__config, 2, 0)
			self.__config = self.__updatebyte(self.__config, 3, 1)
		if rate == 18:
			self.__config = self.__updatebyte(self.__config, 2, 1)
			self.__config = self.__updatebyte(self.__config, 3, 1)

		self.writeRegister(self.__address, self.__config)
		return
