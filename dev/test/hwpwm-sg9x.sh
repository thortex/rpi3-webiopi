#!/bin/bash 

# Products: 
#   http://www.towerpro.com.tw/product/sg92r-7/
#   http://www.towerpro.com.tw/product/sg90-analog/
#     PWM Cycle     : 20ms (= 50Hz)
# PWM Cycle is calculated with (freq / period) = 50,000/1,000 = 50 [Hz]
freq=50000
period=1000
#     Pulse Width   : 0.5ms through 2.4ms
#     control angle : -90 through +90 degree
#     Signals       : Orange=Pulse, Red=Vcc, Brown=Ground
#                   : Vcc = +5.0V
#                   : Pulse = PWM_CLK-enabled GPIO ports.
#     Notes         : 1000uF and 0.1uF capacitors are recommended for 
#                     Vcc-GND. 
m090=120   # -90 degree
n000=72    #   0 degree
p090=25    # +90 degree
wait=1     # delay for steps
duty=$p090 # initial value

# configuration
user=webiopi            # login username 
pass=raspberry          # login password
ipadr=localhost         # webiopi server ip address
port=8000               # webiopi server port number
ch=0                    # PWM Ch# [0 or 1]
# Ch#0: GPIO 12 or 18
# Ch#1: GPIO 13 or 19
pin=18                  # hardware-PWM-enabled GPIO port number

# set clock source
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
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/freq/$freq

# set M/S mode [optional]
# 0: PWM mode 
# 1: M/S mode
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/msmode/1

# set GPIO port
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/port/$pin

# set period
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/period/$period

# set duty
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/duty/$duty

# set output to enable
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/enable

# set duty
for ((i=p090; i<m090; i+=1)); do
 curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/duty/$i
 sleep $wait 
done

# set output to disable
curl -X POST -u $user:$pass http://$ipadr:$port/GPIO/$ch/hwpwm/output/disable
