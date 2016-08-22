import json
from webiopi.utils import logger

M_PLAIN = "text/plain"
M_JSON  = "application/json"

def jsonDumps(obj):
    if logger.debugEnabled():
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        return json.dumps(obj)
    
def str2bool(value):
    return (value == "1") or (value == "true") or (value == "True") or (value == "yes") or (value == "Yes")

def toint(value):
    if isinstance(value, str):
        if value.startswith("0b"):
            return int(value, 2)
        elif value.startswith("0x"):
            return int(value, 16)
        else:
            return int(value)
    return value

        
def signInteger(value, bitcount):
    if value & (1<<(bitcount-1)):
        return value - (1<<bitcount)
    return value
