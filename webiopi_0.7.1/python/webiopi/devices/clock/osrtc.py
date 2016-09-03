#   Copyright 2014 Andreas Riegg - t-h-i-n-x.net
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
#
#   Changelog
#
#   1.0    2014-09-02    Initial release.
#
#   Usage remarks
#
#   - The driver just uses the system clock as available within standard
#     Python. As standard Python does not support setting the system time,
#     this functionality is not available.
#
#   Implementation remarks
#
#   - All __set... methods are not reimplemented, so calling them will lead
#     to the intended NotImplementedError. Dow uses ISO format (1..7).


from webiopi.devices.clock import Clock
from datetime import datetime


class OsClock(Clock):
    
#---------- Class initialisation ----------

    def __init__(self):
        Clock.__init__(self)


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "OsClock"

    def close(self):
        return
    
    
#---------- Clock abstraction related methods ----------

    def __getSec__(self):
        return (datetime.now()).second

    def __getMin__(self):
        return (datetime.now()).minute

    def __getHrs__(self):
        return (datetime.now()).hour

    def __getDay__(self):
        return (datetime.now()).day

    def __getMon__(self):
        return (datetime.now()).month

    def __getYrs__(self):
        return (datetime.now()).year

    def __getDow__(self):
        return (datetime.now()).isoweekday()


#---------- Clock default re-implementations ----------

    def __getDateTime__(self):
        return datetime.now()

    def __getDate__(self):
        return (datetime.now()).date()

    def __getTime__(self):
        return (datetime.now()).time()


