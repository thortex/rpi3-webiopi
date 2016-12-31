#!/usr/bin/python

from webiopi.clients import *
from time import sleep

# Create a WebIOPi client you want to use.
#client = PiHttpClient("192.168.1.234")
#client = PiHttpClient("192.168.0.4")
#client = PiMixedClient("192.168.1.234")
client = PiCoapClient("224.0.1.123")
#client = PiCoapClient("192.168.0.4")
#client = PiMulticastClient()

# enable, if you use authentication method.
#client.setCredentials("webiopi", "raspberry")

# RPi native GPIO
gpio = NativeGPIO(client)
gpio.setFunction(25, "out")
state = 1

while True:
    # toggle digital state
    if state != 0:
        state = 0
    else:
        state = 1
    print ("GPIO port 25 value: %d" % state)
    gpio.digitalWrite(25, state)
    sleep(5)
