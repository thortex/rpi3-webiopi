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
import socket

from webiopi.utils.config import Config
from webiopi.utils import loader
from webiopi.utils import logger
from webiopi.utils import crypto
from webiopi.devices import manager
from webiopi.protocols import rest
from webiopi.protocols import http
from webiopi.protocols import coap
from webiopi.devices.digital.gpio import NativeGPIO

def getLocalIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 53))
            host = s.getsockname()[0]
            s.close()
            return host 
        except:
            return "localhost"

class Server():
    def __init__(self, port=8000, coap_port=5683, login=None, password=None, passwdfile=None, configfile=None, scriptfile=None):
        self.host = getLocalIP()
        self.gpio = NativeGPIO()
        self.restHandler = rest.RESTHandler()
        manager.addDeviceInstance("GPIO", self.gpio, [])

        if configfile != None:
            logger.info("Loading configuration from %s" % configfile)
            config = Config(configfile)
        else:
            config = Config()
            
        self.gpio.addSetups(config.items("GPIO"))
        self.gpio.addResets(config.items("~GPIO"))
        self.gpio.setup()
        
        devices = config.items("DEVICES")
        for (name, params) in devices:
            values = params.split(" ")
            driver = values[0];
            args = {}
            i = 1
            while i < len(values):
                (arg, val) = values[i].split(":")
                args[arg] = val
                i+=1
            manager.addDevice(name, driver, args)
        

        if scriptfile != None:
            scriptname = scriptfile.split("/")[-1].split(".")[0]
            loader.loadScript(scriptname, scriptfile, self.restHandler)    
        
        scripts = config.items("SCRIPTS")
        for (name, source) in scripts:
            loader.loadScript(name, source, self.restHandler)
        
        self.restHandler.device_mapping = config.getboolean("REST", "device-mapping", True)
        self.gpio.post_value = config.getboolean("REST", "gpio-post-value", True)
        self.gpio.post_function = config.getboolean("REST", "gpio-post-function", True)
        exports = config.get("REST", "gpio-export", None)
        if exports != None:
            self.gpio.export = [int(s) for s in exports.split(",")]
        self.restHandler.export = self.gpio.export
        
        http_port = config.getint("HTTP", "port", port)
        http_enabled = config.getboolean("HTTP", "enabled", http_port > 0)
        http_passwdfile = config.get("HTTP", "passwd-file", passwdfile)
        context = config.get("HTTP", "context", None)
        docroot = config.get("HTTP", "doc-root", None)
        index = config.get("HTTP", "welcome-file", None)
            
        coap_port = config.getint("COAP", "port", coap_port)
        coap_enabled = config.getboolean("COAP", "enabled", coap_port > 0)
        coap_multicast = config.getboolean("COAP", "multicast", coap_enabled)

        routes = config.items("ROUTES")
        for (source, destination) in routes:
            self.restHandler.addRoute(source, destination)
    
        auth = None
        if http_passwdfile != None:
            if os.path.exists(http_passwdfile):
                f = open(http_passwdfile)
                auth = f.read().strip(" \r\n")
                f.close()
                if len(auth) > 0:
                    logger.info("Access protected using %s" % http_passwdfile)
                else:
                    logger.info("Passwd file %s is empty" % http_passwdfile)
            else:
                logger.error("Passwd file %s not found" % http_passwdfile)
            
        elif login != None or password != None:
            auth = crypto.encryptCredentials(login, password)
            logger.info("Access protected using login/password")
            
        if auth == None or len(auth) == 0:
            logger.warn("Access unprotected")
        
        realm = config.get("HTTP", "prompt", None)
        
        if http_enabled:
            self.http_server = http.HTTPServer(self.host, http_port, self.restHandler, context, docroot, index, auth, realm)
        else:
            self.http_server = None
        
        if coap_enabled:
            self.coap_server = coap.COAPServer(self.host, coap_port, self.restHandler)
            if coap_multicast:
                self.coap_server.enableMulticast()
        else:
            self.coap_server = None
    
    def addMacro(self, macro):
        self.restHandler.addMacro(macro)
        
    def stop(self):
        if self.http_server:
            self.http_server.stop()
        if self.coap_server:
            self.coap_server.stop()
        loader.unloadScripts()
        manager.closeDevices()



