#!/bin/sh
CC=arm-linux-gnueabihf-gcc

$CC -g -Wall -o webiopi-gpio-test gpio.c pwm.c cpuinfo.c gpio-test.c -lpthread
