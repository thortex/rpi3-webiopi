#!/bin/bash 

# configuration
user=webiopi        # login username 
pass=raspberry      # login password
ipadr=127.0.0.1     # webiopi server ip address
port=8000           # webiopi server port number
pin=4               # GPIO port number
iter=3              # iteration
# set specified GPIO port function to pwm mode.
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/pwm && echo
curl -u $user:$pass http://$ipadr:$port/GPIO/$pin/function && echo 

for (( c=0; c < $iter ; c++ )) ; do
    # S
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseFreq/3 && echo
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.5 && echo
    sleep 0.8
    # pause
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.0 && echo
    sleep 0.2
    # O
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseFreq/1 && echo
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.5 && echo
    sleep 2.8
    # pause
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.0 && echo
    sleep 0.2
    # S
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseFreq/3 && echo
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.5 && echo
    sleep 0.8
    # pause
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.0 && echo
    sleep 2
done

# disable pwm.
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/in && echo
