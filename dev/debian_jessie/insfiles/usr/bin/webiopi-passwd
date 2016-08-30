#!/usr/bin/python
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

import sys
file = None

print("WebIOPi passwd file generator")
if len(sys.argv)  == 2:
    file = sys.argv[1]
    if file == "--help" or file == "-h":
        print("Usage: webiopi-passwd [--help|file]")
        print("Compute and display hash used by WebIOPi for Authentication")
        print("Login and Password are prompted")
        print("\t--help\tDisplay this help")
        print("\t-h")
        print("\tfile\tSave hash to file")
        sys.exit()
else:
    file = "/etc/webiopi/passwd"       

f = open(file, "w")
_LOGIN      = "Enter Login: "
_PASSWORD   = "Enter Password: "
_CONFIRM    = "Confirm password: "
_DONTMATCH  = "Passwords don't match !"

import getpass
try:
    login = raw_input(_LOGIN)
except NameError:
    login = input(_LOGIN)
password = getpass.getpass(_PASSWORD)
password2 = getpass.getpass(_CONFIRM)
while password != password2:
    print(_DONTMATCH)
    password = getpass.getpass(_PASSWORD)
    password2 = getpass.getpass(_CONFIRM)

from webiopi.utils.crypto import encryptCredentials
auth = encryptCredentials(login, password)
print("\nHash: %s" % auth)
if file:
    f.write(auth)
    f.close()
    print("Saved to %s" % file)
