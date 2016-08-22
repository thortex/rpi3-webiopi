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


from time import sleep
 
from webiopi.utils.version import BOARD_REVISION, VERSION
from webiopi.utils.logger import setInfo, setDebug, info, debug, warn, error, exception
from webiopi.utils.thread import runLoop
from webiopi.server import Server
from webiopi.devices.instance import deviceInstance
from webiopi.decorators.rest import macro

from webiopi.devices import bus as _bus


try:
    import _webiopi.GPIO as GPIO
except:
    pass


setInfo()
_bus.checkAllBus()
