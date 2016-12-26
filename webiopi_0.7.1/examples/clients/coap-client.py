#!/usr/bin/python 
from webiopi.protocols.coap import *
from time import sleep

client = COAPClient()
#print "Sending function post request...\n"
# multicast
client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/function/out"))
# unicast
#client.sendRequest(COAPPost("coap://192.168.0.4/GPIO/25/function/out"))
state = True

while True: 
    #print "Sending value change request...\n"
    # multicast
    response = client.sendRequest(COAPPost("coap://224.0.1.123/GPIO/25/value/%d" % state))
    # unicast
    #response = client.sendRequest(COAPPost("coap://192.168.0.4/GPIO/25/value/%d" % state))
    if response:
        print("Received response:\n%s" % response)
        state = not state
    else:
        print("No response received")
    sleep(0.5)
