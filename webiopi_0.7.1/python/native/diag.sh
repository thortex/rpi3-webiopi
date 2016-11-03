#!/bin/sh -x
CC=arm-linux-gnueabihf-gcc

$CC -Wall -o webiopi-diag gpio.c pwm.c cpuinfo.c diag.c -lpthread
