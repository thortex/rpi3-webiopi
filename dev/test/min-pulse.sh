#!/bin/bash 

# configuration
user=webiopi        # login username 
pass=raspberry      # login password
ipadr=127.0.0.1     # webiopi server ip address
port=8000           # webiopi server port number
pin=4               # GPIO port number
freq=0.01           # frequency [100s]

if [ "$1" != "" ] ; then
    freq=$1
fi
echo "Frequency is $freq [Hz]"

# function
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/pwm && echo
curl -u $user:$pass http://$ipadr:$port/GPIO/$pin/function && echo 
# pulse freq
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseFreq/$freq && echo
curl -u $user:$pass http://$ipadr:$port/GPIO/$pin/freq && echo
# pulse ratio
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.5 && echo
curl -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulse && echo
# wait for 300sec
sleep 300
# disable pwm.
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/in && echo
