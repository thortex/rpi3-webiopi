import imp
from webiopi.utils import logger
from webiopi.utils import types
from webiopi.devices.instance import DEVICES

from webiopi.devices import serial, digital, analog, sensor, shield

PACKAGES = [serial, digital, analog, sensor, shield]
def findDeviceClass(name):
    for package in PACKAGES:
        if hasattr(package, name):
            return getattr(package, name)
        if hasattr(package, "DRIVERS"):
            for driver in package.DRIVERS:
                if name in package.DRIVERS[driver]:
                    (fp, pathname, stuff) = imp.find_module(package.__name__.replace(".", "/") + "/" + driver)
                    module = imp.load_module(driver, fp, pathname, stuff)
                    return getattr(module, name)
    return None

def addDevice(name, device, args):
    devClass = findDeviceClass(device)
    if devClass == None:
        raise Exception("Device driver not found for %s" % device)
    if len(args) > 0:
        dev = devClass(**args)
    else:
        dev = devClass()
    addDeviceInstance(name, dev, args)

def addDeviceInstance(name, dev, args):
    funcs = {"GET": {}, "POST": {}}
    for att in dir(dev):
        func = getattr(dev, att)
        if callable(func) and hasattr(func, "routed"):
            if name == "GPIO":
                logger.debug("Mapping %s.%s to REST %s /GPIO/%s" % (dev, att, func.method, func.path))
            else:
                logger.debug("Mapping %s.%s to REST %s /devices/%s/%s" % (dev, att, func.method, name, func.path))
            funcs[func.method][func.path] = func
    
    DEVICES[name] = {'device': dev, 'functions': funcs}
    if name == "GPIO":
        logger.info("GPIO - Native mapped to REST API /GPIO")
    else:
        logger.info("%s - %s mapped to REST API /devices/%s" % (dev.__family__(), dev, name))
        
def closeDevices():
    devices = [k for k in DEVICES.keys()]
    for name in devices:
        device = DEVICES[name]["device"]
        logger.debug("Closing device %s - %s" %  (name, device))
        del DEVICES[name]
        device.close()

def getDevicesJSON(compact=False):
    devname = "name"
    devtype = "type"
    
    devices = []
    for devName in DEVICES:
        if devName == "GPIO":
            continue
        instance = DEVICES[devName]["device"]
        if hasattr(instance, "__family__"):
            family = instance.__family__()
            if isinstance(family, str):
                devices.append({devname: devName, devtype:family})
            else:
                for fam in family:
                    devices.append({devname: devName, devtype:fam})
                    
        else:
            devices.append({devname: devName, type:instance.__str__()})

    return types.jsonDumps(sorted(devices, key=lambda dev: dev[devname]))

