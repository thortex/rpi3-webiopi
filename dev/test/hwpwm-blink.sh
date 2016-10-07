#!/bin/bash 

if [ "x$4" == "x" ] ; then
    echo "Usage $0 freq period duty wait[sec]"
    exit;
fi

freq=$1
period=$2
duty=$3
wait=$4

# configuration
user=webiopi            # login username 
pass=raspberry          # login password
ipadr=raspberrypi.local # webiopi server ip address
port=8000               # webiopi server port number
ch=0                    # PWM Ch# [0 or 1]
# Ch#0: GPIO 12 or 18
# Ch#1: GPIO 13 or 19
pin=18                  # hardware-PWM-enabled GPIO port number

# set clock source
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/clock
# [osc, plla, pllc, plld, or pllh]
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/clock/osc

# set frequency
# valid frequency ranges: 
# ----------------------------------------
#           min             max
# ----------------------------------------
#  osc      4,688 through    19,200,000 Hz
# plla    158,730 through   650,000,000 Hz
# pllc     48,840 through   200,000,000 Hz
# plld    122,100 through   500,000,000 Hz
# pllh     52,747 through   216,000,000 Hz
# ----------------------------------------
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/freq
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/freq/$freq

# set M/S mode [optional]
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/msmode
# 0: PWM mode 
# 1: M/S mode
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/msmode/1

# set polarity [optional]
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/polarity
# 0: normal
# 1: reverse
#curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/polarity/0

# set GPIO port
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/port
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/port/$pin

# set period
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/period
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/period/$period

# set duty
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/duty
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/duty/$duty

# set output to enable
#curl         -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output
# enable or disable
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/enable

# set duty
#for ((i=0; i<1024; i+=16)); do
#    curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/duty/$i
#done

# set output to disable
#curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/disable

sleep $wait 

# set output to enable
#curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/enable

# set frequency
#curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/freq/50000

#sleep 3 

# set output to disable
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/disable
