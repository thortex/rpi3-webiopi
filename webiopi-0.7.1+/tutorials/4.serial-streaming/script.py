import webiopi

# import Serial driver
from webiopi.devices.serial import Serial

# initialize Serial driver
serial = Serial("ttyACM0", 9600)
sensors = [0 for a in range(6)]

def setup():
    # empty input buffer before starting processing
    while (serial.available() > 0):
        serial.readString()

def loop():
    if (serial.available() > 0):
        data = serial.readString()     # read available data
        lines = data.split("\r\n")     # split lines
        count = len(lines)             # count lines

        lines = lines[0:count-1]       # remove last item from split which is empty

        # process each complete line
        for pair in lines:
            cv = pair.split("=")       # split channel/value
            channel = int(cv[0])
            value = int(cv[1])
            sensors[channel] = value   # store value

    webiopi.sleep(1)


# this macro scales sensor value and returns it as percent string
@webiopi.macro
def getSensor(channel):
    percent = (sensors[int(channel)] / 1024.0) * 100.0
    return "%.2f%%" % percent

