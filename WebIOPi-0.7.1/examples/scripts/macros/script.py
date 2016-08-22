# Imports
import webiopi
import time

# Enable debug output
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

SWITCH = 21
SERVO  = 23
LED0   = 24
LED1   = 25

# Called by WebIOPi at script loading
def setup():
    webiopi.debug("Script with macros - Setup")
    # Setup GPIOs
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.PWM)
    GPIO.setFunction(LED0, GPIO.PWM)
    GPIO.setFunction(LED1, GPIO.OUT)
    
    GPIO.pwmWrite(LED0, 0.5)        # set to 50% ratio
    GPIO.pwmWriteAngle(SERVO, 0)    # set to 0 (neutral)
    GPIO.digitalWrite(LED1, GPIO.HIGH)
    
    gpio0 = webiopi.deviceInstance("gpio0")
    gpio0.digitalWrite(0, 0)

# Looped by WebIOPi
def loop():
    # Toggle LED each 5 seconds
    value = not GPIO.digitalRead(LED1)
    GPIO.digitalWrite(LED1, value)
    webiopi.sleep(5)        

# Called by WebIOPi at server shutdown
def destroy():
    webiopi.debug("Script with macros - Destroy")
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(LED0, GPIO.IN)
    GPIO.setFunction(LED1, GPIO.IN)
    gpio0 = webiopi.deviceInstance("gpio0")
    gpio0.digitalWrite(0, 1)

# A macro which says hello
@webiopi.macro
def HelloWorld(first, last):
    webiopi.debug("HelloWorld(%s, %s)" % (first, last))
    return "Hello %s %s !" % (first, last)

# A macro without args which return nothing
@webiopi.macro
def PrintTime():
    webiopi.debug("PrintTime: " + time.asctime())

