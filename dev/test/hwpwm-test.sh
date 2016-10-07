#!/bin/sh 

# LED blinking test by RPi hardware PWM

# 25 Hz blinking
./hwpwm-blink.sh 5000 200 100 3
sleep 1

# 5 Hz blinking
./hwpwm-blink.sh 5000 1000 500 3
sleep 1

# 2.5 Hz blinking
./hwpwm-blink.sh 5000 2000 1000 3
sleep 1

# 1 Hz blinking
./hwpwm-blink.sh 5000 5000 2500 3
sleep 1

# 0.5 Hz blinking
./hwpwm-blink.sh 5000 10000 5000 6
sleep 1
