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
import socket
import threading
import codecs
import mimetypes as mime
import logging

from webiopi.utils.version import VERSION_STRING, PYTHON_MAJOR
from webiopi.utils.logger import info, exception
from webiopi.utils.crypto import encrypt
from webiopi.utils.types import str2bool

if PYTHON_MAJOR >= 3:
    import http.server as BaseHTTPServer
else:
    import BaseHTTPServer

try :
    import _webiopi.GPIO as GPIO
except:
    pass

WEBIOPI_DOCROOT = "/usr/share/webiopi/htdocs"

class HTTPServer(BaseHTTPServer.HTTPServer, threading.Thread):
    if socket.has_ipv6:
        address_family = socket.AF_INET6

    def __init__(self, host, port, handler, context, docroot, index, auth=None, realm=None):
        try:
            BaseHTTPServer.HTTPServer.__init__(self, ("", port), HTTPHandler)
        except:
            self.address_family = socket.AF_INET
            BaseHTTPServer.HTTPServer.__init__(self, ("", port), HTTPHandler)

        threading.Thread.__init__(self, name="HTTPThread")
        self.host = host
        self.port = port

        if context:
            self.context = context
            if not self.context.startswith("/"):
                self.context = "/" + self.context
            if not self.context.endswith("/"):
                self.context += "/"
        else:
            self.context = "/"

        self.docroot = docroot

        if index:
            self.index = index
        else:
            self.index = "index.html"
            
        self.handler = handler
        self.auth = auth
        if (realm == None):
            self.authenticateHeader = "Basic realm=webiopi"
        else:
            self.authenticateHeader = "Basic realm=%s" % realm

        self.running = True
        self.start()
            
    def get_request(self):
        sock, addr = self.socket.accept()
        sock.settimeout(10.0)
        return (sock, addr)

    def run(self):
        info("HTTP Server binded on http://%s:%s%s" % (self.host, self.port, self.context))
        try:
            self.serve_forever()
        except Exception as e:
            if self.running == True:
                exception(e)
        info("HTTP Server stopped")

    def stop(self):
        self.running = False
        self.server_close()

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    logger = logging.getLogger("HTTP")

    def log_message(self, fmt, *args):
        pass
    
    def log_error(self, fmt, *args):
        pass
        
    def version_string(self):
        return VERSION_STRING
    
    def checkAuthentication(self):
        if self.server.auth == None or len(self.server.auth) == 0:
            return True
        
        authHeader = self.headers.get('Authorization')
        if authHeader == None:
            return False
        
        if not authHeader.startswith("Basic "):
            return False
        
        auth = authHeader.replace("Basic ", "")
        if PYTHON_MAJOR >= 3:
            auth_hash = encrypt(auth.encode())
        else:
            auth_hash = encrypt(auth)
            
        if auth_hash == self.server.auth:
            return True
        return False

    def requestAuthentication(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", self.server.authenticateHeader)
        self.end_headers();
        
    
    def logRequest(self, code):
        self.logger.debug('"%s %s %s" - %s %s (Client: %s <%s>)' % (self.command, self.path, self.request_version, code, self.responses[code][0], self.client_address[0], self.headers["User-Agent"]))
    
    def sendResponse(self, code, body=None, contentType="text/plain"):
        if code >= 400:
            if body != None:
                self.send_error(code, body)
            else:
                self.send_error(code)
        else:
            self.send_response(code)
            self.send_header("Cache-Control", "no-cache")
            if body != None:
                encodedBody = body.encode();
                self.send_header("Content-Type", contentType);
                self.send_header("Content-Length", len(encodedBody));
                self.end_headers();
                self.wfile.write(encodedBody)
        self.logRequest(code)

    def findFile(self, filepath):
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                filepath += "/" + self.server.index
                if os.path.exists(filepath):
                    return filepath
            else:
                return filepath
        return None
        
                
    def serveFile(self, relativePath):
        if self.server.docroot != None:
            path = self.findFile(self.server.docroot + "/" + relativePath)
            if path == None:
                path = self.findFile("./" + relativePath)

        else:
            path = self.findFile("./" + relativePath)                
            if path == None:
                path = self.findFile(WEBIOPI_DOCROOT + "/" + relativePath)

        if path == None and (relativePath.startswith("webiopi.") or relativePath.startswith("jquery")):
            path = self.findFile(WEBIOPI_DOCROOT + "/" + relativePath)

        if path == None:
            return self.sendResponse(404, "Not Found")

        realPath = os.path.realpath(path)
        
        if realPath.endswith(".py"):
            return self.sendResponse(403, "Not Authorized")
        
        if not (realPath.startswith(os.getcwd()) 
                or (self.server.docroot and realPath.startswith(self.server.docroot))
                or realPath.startswith(WEBIOPI_DOCROOT)):
            return self.sendResponse(403, "Not Authorized")
        
        (contentType, encoding) = mime.guess_type(path)
        f = codecs.open(path, encoding=encoding)
        data = f.read()
        f.close()
        self.send_response(200)
        self.send_header("Content-Type", contentType);
        self.send_header("Content-Length", os.path.getsize(realPath))
        self.end_headers()
        self.wfile.write(data)
        self.logRequest(200)
        
    def processRequest(self):
        self.request.settimeout(None)
        if not self.checkAuthentication():
            return self.requestAuthentication()
        
        request = self.path.replace(self.server.context, "/").split('?')
        relativePath = request[0]
        if relativePath[0] == "/":
            relativePath = relativePath[1:]
            
        if relativePath == "webiopi" or relativePath == "webiopi/":
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
            return

        params = {}
        if len(request) > 1:
            for s in request[1].split('&'):
                if s.find('=') > 0:
                    (name, value) = s.split('=')
                    params[name] = value
                else:
                    params[s] = None
        
        compact = False
        if 'compact' in params:
            compact = str2bool(params['compact'])

        try:
            result = (None, None, None)
            if self.command == "GET":
                result = self.server.handler.do_GET(relativePath, compact)
            elif self.command == "POST":
                length = 0
                length_header = 'content-length'
                if length_header in self.headers:
                    length = int(self.headers[length_header])
                result = self.server.handler.do_POST(relativePath, self.rfile.read(length), compact)
            else:
                result = (405, None, None)
                
            (code, body, contentType) = result
            
            if code > 0:
                self.sendResponse(code, body, contentType)
            else:
                if self.command == "GET":
                    self.serveFile(relativePath)
                else:
                    self.sendResponse(404)

        except (GPIO.InvalidDirectionException, GPIO.InvalidChannelException, GPIO.SetupException) as e:
            self.sendResponse(403, "%s" % e)
        except ValueError as e:
            self.sendResponse(403, "%s" % e)
        except Exception as e:
            self.sendResponse(500)
            raise e
            
    def do_GET(self):
        self.processRequest()

    def do_POST(self):
        self.processRequest()
