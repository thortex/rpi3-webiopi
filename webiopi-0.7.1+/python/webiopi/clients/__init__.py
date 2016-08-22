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

from webiopi.utils.logger import LOGGER
from webiopi.utils.version import PYTHON_MAJOR
from webiopi.utils.crypto import encodeCredentials
from webiopi.protocols.coap import COAPClient, COAPGet, COAPPost, COAPPut, COAPDelete

if PYTHON_MAJOR >= 3:
    import http.client as httplib
else:
    import httplib

class PiMixedClient():
    def __init__(self, host, port=8000, coap=5683):
        self.host = host
        if coap > 0:
            self.coapport = coap
            self.coapclient = COAPClient()
        else:
            self.coapclient = None
        if port > 0:
            self.httpclient = httplib.HTTPConnection(host, port)
        else:
            self.httpclient = None
        self.forceHttp = False
        self.coapfailure = 0
        self.maxfailure = 2
        self.auth= None;
    
    def setCredentials(self, login, password):
        self.auth = "Basic " + encodeCredentials(login, password)
        
    def sendRequest(self, method, uri):
        if self.coapclient != None and not self.forceHttp:
            if method == "GET":
                response = self.coapclient.sendRequest(COAPGet("coap://%s:%d%s" % (self.host, self.coapport, uri)))
            elif method == "POST":
                response = self.coapclient.sendRequest(COAPPost("coap://%s:%d%s" % (self.host, self.coapport, uri)))

            if response:
                return str(response.payload)
            elif self.httpclient != None:
                self.coapfailure += 1
                print("No CoAP response, fall-back to HTTP")
                if (self.coapfailure > self.maxfailure):
                    self.forceHttp = True
                    self.coapfailure = 0
                    print("Too many CoAP failure forcing HTTP")
        
        if self.httpclient != None:
            headers = {}
            if self.auth != None:
                headers["Authorization"] = self.auth
            
            self.httpclient.request(method, uri, None, headers)
            response = self.httpclient.getresponse()
            if response.status == 200:
                data = response.read()
                return data
            elif response.status == 401:
                raise Exception("Missing credentials")
            else:
                raise Exception("Unhandled HTTP Response %d %s" % (response.status, response.reason))

        raise Exception("No data received")

class PiHttpClient(PiMixedClient):
    def __init__(self, host, port=8000):
        PiMixedClient.__init__(self, host, port, -1)

class PiCoapClient(PiMixedClient):
    def __init__(self, host, port=5683):
        PiMixedClient.__init__(self, host, -1, port)

class PiMulticastClient(PiMixedClient):
    def __init__(self, port=5683):
        PiMixedClient.__init__(self, "224.0.1.123", -1, port)

class RESTAPI():
    def __init__(self, client, path):
        self.client = client
        self.path = path
        
    def sendRequest(self, method, path):
        return self.client.sendRequest(method, self.path + path)
        
class Macro(RESTAPI):
    def __init__(self, client, name):
        RESTAPI.__init__(self, client, "/macros/" + name + "/")
        
    def call(self, *args):
        values = ",".join(["%s" % i for i in args])
        if values == None:
            values = ""
        return self.sendRequest("POST", values)

class Device(RESTAPI):
    def __init__(self, client, name, category):
        RESTAPI.__init__(self, client, "/devices/" + name + "/" + category)

class GPIO(Device):
    def __init__(self, client, name):
        Device.__init__(self, client, name, "digital")
        
    def getFunction(self, channel):
        return self.sendRequest("GET", "/%d/function" % channel)

    def setFunction(self, channel, func):
        return self.sendRequest("POST", "/%d/function/%s" % (channel, func))
        
    def digitalRead(self, channel):
        return int(self.sendRequest("GET", "/%d/value" % channel))

    def digitalWrite(self, channel, value):
        return int(self.sendRequest("POST", "/%d/value/%d" % (channel, value)))
    
    def portRead(self):
        return int(self.sendRequest("GET", "/integer"))

    def portWrite(self, value):
        return int(self.sendRequest("POST", "/integer/%d" % value))

class NativeGPIO(GPIO):
    def __init__(self, client):
        RESTAPI.__init__(self, client, "/GPIO")

class ADC(Device):
    def __init__(self, client, name):
        Device.__init__(self, client, name, "analog")
        
    def read(self, channel):
        return float(self.sendRequest("GET", "/%d/integer" % channel))

    def readFloat(self, channel):
        return float(self.sendRequest("GET", "/%d/float" % channel))

    def readVolt(self, channel):
        return float(self.sendRequest("GET", "/%d/volt" % channel))

class DAC(ADC):
    def __init__(self, client, name):
        Device.__init__(self, client, name, "analog")
        
    def write(self, channel, value):
        return float(self.sendRequest("POST", "/%d/integer/%d" % (channel, value)))
                     
    def writeFloat(self, channel, value):
        return float(self.sendRequest("POST", "/%d/float/%f" % (channel, value)))
                     
    def writeVolt(self, channel, value):
        return float(self.sendRequest("POST", "/%d/volt/%f" % (channel, value)))
                     
class PWM(DAC):
    def __init__(self, client, name):
        Device.__init__(self, client, name, "pwm")
        
    def readAngle(self, channel, value):
        return float(self.sendRequest("GET", "/%d/angle" % (channel)))
                     
    def writeAngle(self, channel, value):
        return float(self.sendRequest("POST", "/%d/angle/%f" % (channel, value)))
                     
class Sensor(Device):
    def __init__(self, client, name):
        Device.__init__(self, client, name, "sensor")
        
class Temperature(Sensor):
    def getKelvin(self):
        return float(self.sendRequest("GET", "/temperature/k"))

    def getCelsius(self):
        return float(self.sendRequest("GET", "/temperature/c"))

    def getFahrenheit(self):
        return float(self.sendRequest("GET", "/temperature/f"))
    
class Pressure(Sensor):
    def getPascal(self):
        return float(self.sendRequest("GET", "/pressure/pa"))

    def getHectoPascal(self):
        return float(self.sendRequest("GET", "/pressure/hpa"))
    
class Luminosity(Sensor):
    def getLux(self):
        return float(self.sendRequest("GET", "/luminosity/lux"))
    
class Distance(Sensor):
    def getMillimeter(self):
        return float(self.sendRequest("GET", "/distance/mm"))

    def getCentimeter(self):
        return float(self.sendRequest("GET", "/distance/cm"))

    def getInch(self):
        return float(self.sendRequest("GET", "/distance/in"))

