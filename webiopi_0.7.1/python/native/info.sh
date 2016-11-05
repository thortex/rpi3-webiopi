#!/bin/sh -x
CC=arm-linux-gnueabihf-gcc

$CC -g -Wall -o webiopi-info gpio.c pwm.c cpuinfo.c diag.c -lpthread
