import re
import sys

try:
    import _webiopi.GPIO as GPIO
except:
    pass

VERSION         = '0.7.1'
VERSION_STRING  = "YA-WebIOPi/%s/Python%d.%d" % (VERSION, sys.version_info.major, sys.version_info.minor)
PYTHON_MAJOR    = sys.version_info.major
BOARD_REVISION  = 0

_MAPPING = [[], [], [], []]
_MAPPING[1] = ["V33", "V50", 0, "V50", 1, "GND", 4, 14, "GND", 15, 17, 18, 21, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7, "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC"]
_MAPPING[2] = ["V33", "V50", 2, "V50", 3, "GND", 4, 14, "GND", 15, 17, 18, 27, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7, "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC", "DNC"]
_MAPPING[3] = ["V33", "V50", 2, "V50", 3, "GND", 4, 14, "GND", 15, 17, 18, 27, "GND", 22, 23, "V33", 24, 10, "GND", 9, 25, 11, 8, "GND", 7, "DNC", "DNC" , 5, "GND", 6, 12, 13, "GND", 19, 16, 26, 20, "GND", 21]

try:
    BOARD_REVISION = GPIO.BOARD_REVISION
except:
    pass

MAPPING = _MAPPING[BOARD_REVISION]
