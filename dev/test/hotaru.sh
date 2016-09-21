#!/bin/bash 

# configuration
user=webiopi        # login username 
pass=raspberry      # login password
ipadr=127.0.0.1     # webiopi server ip address
port=8000           # webiopi server port number
pin=4               # GPIO port number

# default pwm frequency is 50 Hz.

# set specified GPIO port function to pwm mode.
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/pwm
echo

# get the function.
curl -u $user:$pass http://$ipadr:$port/GPIO/$pin/function
echo

for (( c=0; c < 3 ; c++ )) ; do
    for (( i=0; i<100; i+=5 )) ; do 
	v=`printf "%02d" $i`; 
	curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.$v;
	echo 
    done
    sleep 0.5
    for (( i=99; i>=0 ; i-=5 )) ; do 
	v=`printf "%02d" $i`; 
	curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.$v; 
	echo 
    done
    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/pulseRatio/0.0
    echo 
    sleep 0.7
done
echo

# disable pwm.
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$pin/function/in
echo
