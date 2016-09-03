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
#   1.0    2014-06-04    Initial release.
#   1.1    2014-08-17    Added public NON-REST methods that work with 
#                        naive Python datetime objects and restructured code
#   1.2    2014-09-23    Added driver lookup for class OsClock
#
#   Usage remarks
#
#   - Date formatting is handled according to ISO8601:2004 (aka ISO calendar).
#   - Public NON-REST methods have real Python datetime objects as parameters
#   - All datetime objects are handeled in naive mode as (most) RTC chips do
#     not handle timezione infos. It's up to the user to decide what time gets
#     stored in the chips. It's recommended to use UTC.
#   - Setting date via REST is only possible as full date string to be able 
#     to check calendar consistency
#   - Setting time via REST is handled the same way for consistency and 
#     simplification
#

from webiopi.decorators.rest import request, response
from webiopi.utils.types import toint, M_JSON
from datetime import datetime, date, time


class Clock():

    def __init__(self):
        return

#---------- Abstraction framework contracts ----------
        
    def __family__(self):
        return "Clock"


#---------- Clock abstraction REST implementation ----------
    
    @request("GET", "clock/*")
    @response(contentType=M_JSON)
    def clockWildcard(self):
        return  {"isotime": self.getTimeString(),
                 "isodate": self.getDateString(),
                 "isodow": self.getDow()}
        # {
        # "isotime" = "12:34:56",
        # "isodate" = "2014-05-13",
        # "isodow" = 3
        # }
        
    @request("GET", "clock/datetime")
    @response("%s")
    def getDateTimeString(self):
        return self.__getDateTimeString__()
    
    @request("GET", "clock/date")
    @response("%s")
    def getDateString(self):
        return self.__getDateString__()

    @request("POST", "clock/date/%(value)s")
    @response("%s")
    def setDateString(self, value):
        year, month, day = self.String2DateValues(value)
        newDate = date(year, month, day)
        self.setDate(newDate)
        return self.getDateString()

    @request("GET", "clock/time")
    @response("%s")
    def getTimeString(self):
        return self.__getTimeString__()

    @request("POST", "clock/time/%(value)s")
    @response("%s")
    def setTimeString(self, value):
        hour, minute, second = self.String2TimeValues(value)
        newTime = time(hour, minute, second)
        self.setTime(newTime)
        return self.getTimeString()

    @request("GET", "clock/second")
    @response("%d")
    def getSec(self):
        return self.__getSec__()

    @request("GET", "clock/minute")
    @response("%d")
    def getMin(self):
        return self.__getMin__()

    @request("GET", "clock/hour")
    @response("%d")
    def getHrs(self):
        return self.__getHrs__()

    @request("GET", "clock/dow")
    @response("%d")
    def getDow(self):
        return self.__getDow__()

    @request("POST", "clock/dow/%(value)d")
    @response("%d")
    def setDow(self, value):
        self.checkDow(value)
        self.__setDow__(value)
        return self.getDow()

    @request("GET", "clock/day")
    @response("%d")
    def getDay(self):
        return self.__getDay__()

    @request("GET", "clock/month")
    @response("%d")
    def getMon(self):
        return self.__getMon__()

    @request("GET", "clock/year")
    @response("%d")
    def getYrs(self):
        return self.__getYrs__()


#---------- Clock abstraction NON-REST implementation ----------

    def getDateTime(self):
        return self.__getDateTime__()

    def setDateTime(self, aDatetime):
        return self.__setDateTime__(aDatetime)

    def getDate(self):
        return self.__getDate__()

    def setDate(self, aDate):
        return self.__setDate__(aDate)

    def getTime(self):
        return self.__getTime__()

    def setTime(self, aTime):
        return self.__setTime__(aTime)
  
    
#---------- Clock abstraction contracts ----------
    
    def __getSec__(self):
        raise NotImplementedError

    def __setSec__(self, value):
        raise NotImplementedError

    def __getMin__(self):
        raise NotImplementedError

    def __setMin__(self, value):
        raise NotImplementedError

    def __getHrs__(self):
        raise NotImplementedError

    def __setHrs__(self, value):
        raise NotImplementedError

    def __getDay__(self):
        raise NotImplementedError

    def __setDay__(self, value):
        raise NotImplementedError

    def __getMon__(self):
        raise NotImplementedError

    def __setMon__(self, value):
        raise NotImplementedError

    def __getYrs__(self):
        raise NotImplementedError

    def __setYrs__(self, value):
        raise NotImplementedError

    def __getDow__(self):
        raise NotImplementedError

    def __setDow__(self, value):
        raise NotImplementedError

        
#---------- Clock default implementations ----------
# Rely on reading and writing the base digits, all or some may be reimplemented
# in subclasses for performance improvements by e.g. sequential register access.
# If all methods here that have the __set prefix are reimplemented without using
# any of the __set digit primitives (e.g. __setYrs__()), then these __set methods 
# are not mandatory to be reimplemented in order to avoid the NotImplementedError
# as they will never be called (but __setDow__() IS still needed).

    def __getDateTime__(self):
        return datetime(self.__getYrs__(),
                        self.__getMon__(),
                        self.__getDay__(),
                        self.__getHrs__(),
                        self.__getMin__(),
                        self.__getSec__())  

    def __setDateTime__(self, aDatetime):
        self.checkYear(aDatetime.year)
        self.__setYrs__(aDatetime.year)
        self.__setMon__(aDatetime.month)
        self.__setDay__(aDatetime.day)
        self.__setHrs__(aDatetime.hour)
        self.__setMin__(aDatetime.minute)
        self.__setSec__(aDatetime.second)

    def __getDate__(self):
        return date(self.__getYrs__(),
                    self.__getMon__(),
                    self.__getDay__())

    def __setDate__(self, aDate):
        self.checkYear(aDate.year)
        self.__setYrs__(aDate.year)
        self.__setMon__(aDate.month)
        self.__setDay__(aDate.day)

    def __getTime__(self):
        return time(self.__getHrs__(),
                    self.__getMin__(),
                    self.__getSec__())

    def __setTime__(self, aTime):
        self.__setHrs__(aTime.hour)
        self.__setMin__(aTime.minute)
        self.__setSec__(aTime.second)


#---------- Clock abstraction helpers ----------

    def __getDateTimeString__(self):
        theDateTime = self.__getDateTime__()
        return self.Strings2DateTimeString(
            self.DateValues2String(theDateTime.year, theDateTime.month, theDateTime.day),
            self.TimeValues2String(theDateTime.hour, theDateTime.minute, theDateTime.second))

    def __getDateString__(self):
        theDate = self.__getDate__()
        return self.DateValues2String(theDate.year, theDate.month, theDate.day)

    def __getTimeString__(self):
        theTime = self.__getTime__()
        return self.TimeValues2String(theTime.hour, theTime.minute, theTime.second)

       
#---------- BCD Conversions ----------

    def BcdBits2Int(self, bits):
        if (bits < 0):
            raise NotImplementedError
        elif (bits <= 0xFF):
            # most used case, make it faster
            return (
                    (((bits >> 4)  & 0x0F) * 10) +
                    (bits & 0x0F)
                   )
        elif (bits <= 0xFFFFFFFF):
            # 32 bits, being 8 digits, should be enough ...
            return (
                    (((bits >> 28) & 0x0F) * 10000000) +
                    (((bits >> 24) & 0x0F) * 1000000) +
                    (((bits >> 20) & 0x0F) * 100000) +
                    (((bits >> 16) & 0x0F) * 10000) +
                    (((bits >> 12) & 0x0F) * 1000) +
                    (((bits >> 8)  & 0x0F) * 100) +
                    (((bits >> 4)  & 0x0F) * 10) +
                    (bits & 0x0F)
                   )
        else:
            raise NotImplementedError

    def Int2BcdBits(self, value):
        valueString = "%d" % value
        bcdBits = 0
        digits = len(valueString)
        for i in range(digits):
            bcdBits += int(valueString[i]) << (4 * (digits - 1 - i))
        return bcdBits


#---------- Value checks ----------
    
    def checkYear(self, year):
        # Most RTC chips handle leap years only correct for 21st century
        # so limit allowed year value to this range
        if not year in range(2000,2100):
            raise ValueError("year [%d] out of range [%d..%d]" % (year, 2000, 2099))

    def checkDow(self, dow):
        if not dow in range(1,8):
            raise ValueError("dow [%d] out of range [%d..%d]" % (dow, 1, 7))


#---------- Clock values formatting ----------

    def DateValues2String(self, year, month, day):
        #"2014-05-13"
        return "%04d-%02d-%02d" % (year, month, day)

    def TimeValues2String(self, hour, minute, second):
        #"12:34:56"
        return "%02d:%02d:%02d" % (hour, minute, second)

    def Strings2DateTimeString(self, dateString, timeString):
        #"2014-05-13T12:34:56"
        return "%sT%s" % (dateString, timeString)
    
    def String2DateValues(self, string):
        values = string.split('-')
        year = toint(values[0]) 
        month = toint(values[1]) 
        day = toint(values[2])
        return (year, month, day)

    def String2TimeValues(self, string):
        values = string.split(':')
        hour = toint(values[0]) 
        minute = toint(values[1]) 
        if len(values) > 2:
            second = toint(values[2])
        else:
            second = 0
        return (hour, minute, second)

                        
#---------- Driver lookup ----------
        
DRIVERS = {}
DRIVERS["dsrtc"] = ["DS1307", "DS1337", "DS1338", "DS3231"]
DRIVERS["mcprtc"] = ["MCP7940"]
DRIVERS["osrtc"] = ["OsClock"]
