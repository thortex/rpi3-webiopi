import webiopi
GPIO = webiopi.GPIO # Helper for LOW/HIGH values
HEATER = 7 # Heater plugged on the Expander Pin 7
MIN = 22 # Minimum temperature in celsius
MAX = 24 # Maximum temperature in celsius
AUTO = True

# setup function is automatically called at WebIOPi startup
def setup():
    mcp = webiopi.deviceInstance("mcp") # retrieve the device named "mcp" in the configuration 
    mcp.setFunction(HEATER, GPIO.OUT)

# loop function is repeatedly called by WebIOPi 
def loop():
    if (AUTO):
        tmp = webiopi.deviceInstance("tmp") # retrieve the device named "tmp" in the configuration
        mcp = webiopi.deviceInstance("mcp") # retrieve the device named "mcp" in the configuration 

        celsius = tmp.getCelsius() # retrieve current temperature
        print("Temperature: %f" % celsius)

        # Turn ON heater when passing below the minimum temperature
        if (celsius < MIN):
            mcp.digitalWrite(HEATER, GPIO.HIGH)

        # Turn OFF heater when reaching maximum temperature
        if (celsius >= MAX):
            mcp.digitalWrite(HEATER, GPIO.LOW)

    # gives CPU some time before looping again
    webiopi.sleep(1)

# destroy function is called at WebIOPi shutdown
def destroy():
    mcp = webiopi.deviceInstance("mcp") # retrieve the device named "mcp" in the configuration 
    mcp.digitalWrite(HEATER, GPIO.LOW) # turn off to avoid over heating

# a simple macro to return heater mode
@webiopi.macro
def getMode():
    if (AUTO):
        return "auto"
    return "manual"

# simple macro to set and return heater mode
@webiopi.macro
def setMode(mode):
    global AUTO
    if (mode == "auto"):
        AUTO = True
    elif (mode == "manual"):
        AUTO = False
    return getMode()


