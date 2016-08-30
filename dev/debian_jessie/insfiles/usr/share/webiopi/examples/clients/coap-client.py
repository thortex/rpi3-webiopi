from webiopi.protocols.coap import *
from time import sleep

client = COAPClient()
client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/function/out"))
state = True

while True: 
    response = client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/value/%d" % state))
    if response:
        print("Received response:\n%s" % response)
        state = not state
    else:
        print("No response received")
    sleep(0.5)
