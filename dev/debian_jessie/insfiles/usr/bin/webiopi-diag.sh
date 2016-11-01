#!/bin/sh 

user=webiopi
pass=raspberry
MY_VERSION="1.0.0"
MY_NAME="webiopi-diag"
MY_AUTHOR="Thor Watanabe"
MY_COPY="Apache 2.0"

print_hr(){
    echo ""
    echo ""
    echo "--------------------------------------------------"
    echo "$1"
    echo ""
}

print_usage(){
    echo "Usage: "
    echo "$MY_NAME <webiopi_username> <webiopi_password>"
}

user=$1
pass=$2
if [ "x$user" = "x" ] ; then
    print_usage;
    exit;
fi

if [ "x$pass" = "x" ] ; then
    print_usage;
    exit;
fi

# ------------------------------------------------------------


print_hr "Yet Another WebIOPi+ Diagnostic Tool for Bug Report";
echo "Version: $MY_VERSION"
echo "Author:  $MY_AUTHOR"
echo "License: $MY_COPY"


print_hr "Process Information";
ps aux | grep webiopi | grep -v grep


print_hr "WebIOPi Log Outputs";
egrep -v ' (DEBUG|INFO) ' /var/log/webiopi | tail -100

print_hr "Distribution"
LSB=`which lsb_release`
if [ "$LSB" != "" ] ; then
echo    lsb_release -a
else
    cat /etc/os-release
fi

print_hr "Hardware/Revision"
cat /proc/cpuinfo | egrep '(Hardware|Revision)'

print_hr "Number of Files In htdocs Directory"
find /usr/share/webiopi/htdocs/ | wc -l

print_hr "Debian Package Information"
dpkg -l 'python*-webiopi'

print_hr "Kernel"
uname -a

print_hr "WebIOPi Configuration"
grep -v '^#' /etc/webiopi/config | grep -v '^$'

print_hr "Available python Versions"
ls -l /usr/bin/python*

print_hr "Related Package Information"
dpkg -l '*webiopi' '*setuptools' 'python*-dev' 'python*gpio' 'wiringpi'

print_hr "syslog"
sudo grep python /var/log/syslog

print_hr "HTTP"
host=localhost
port=`cat /etc/webiopi/config| perl -e 'while(<>){last if m/'HTTP'/;} while(<>){if(m/port\s+=\s+(\d+)/){print $1;last;}}'`
echo "Accessing to $host:$port ..."

print_hr "HTTP top page"
(http_proxy="" curl -u $user:$pass http://$host:$port/) | grep WebIOPi 

print_hr "HTTP gpio-header"
(http_proxy="" curl -u $user:$pass http://$host:$port/app/gpio-header) | grep WebIOPi

print_hr "HTTP GPIO Map"
gpio_map=`(http_proxy="" curl -u $user:$pass http://$host:$port/map)`
echo ""
echo $gpio_map | sed -e 's/\[//; s/]//; s/ //g; s/,/\n/g; s/"//g;' | \
    perl -e '$cnt=0;while(<>){chop; $cnt++; if(0==($cnt%2)){printf("%2d  %-6s\n",$cnt,$_);} else {printf("%6s  %2d  ",$_,$cnt);}}'

print_hr "HTTP Board Revision"
(http_proxy="" curl -u $user:$pass http://$host:$port/revision)

print_hr "HTTP WebIOPi Version"
(http_proxy="" curl -u $user:$pass http://$host:$port/version)

print_hr "HTTP Devices"
(http_proxy="" curl -u $user:$pass "http://$host:$port/devices/*")

print_hr "I2C/SPI lsmod"
lsmod | egrep -e '(spi|i2c)'

print_hr "I2C/SPI blacklist"
cat /etc/modprobe.d/raspi-blacklist.conf

print_hr "Boot Configuration"
cat /boot/config.txt  | grep -v '^#' | grep -v '^$'

print_hr "GCC"
gcc --version

print_hr "WebIOPi Package Files for python2"
dpkg -L 'python2-webiopi' | grep -v '\.py$' | egrep -e '(GPIO|egg)'

print_hr "WebIOPi Package Files for python3"
dpkg -L 'python3-webiopi' | grep -v '\.py$' | egrep -e '(GPIO|egg)'

print_hr "Python2 Native Library Information"
native_so=`dpkg -L 'python2-webiopi' | grep -v '\.py$' | egrep -e 'GPIO.so' | head -1`
if [ "$native_so" != "" ] ; then
    readelf -s $native_so | grep -v ' UND '
    readelf -A $native_so
fi

print_hr "Python3 Native Library Information"
native_so=`dpkg -L 'python3-webiopi' | grep -v '\.py$' | egrep -e 'GPIO.so' | head -1`
if [ "$native_so" != "" ] ; then
    readelf -s $native_so | grep -v ' UND '
    readelf -A $native_so
fi

print_hr "SoC Ranges"
range_file=/proc/device-tree/soc/ranges
if [ -f "$range_file" ] ; then 
    cat $range_file | xxd -s 4 -l 4
else
    echo "There is no SoC Range Information"
fi

print_hr "Board Model"
cat /proc/device-tree/model

print_hr "Board Compatible"
cat /proc/device-tree/compatible

print_hr "ifconfig"
ifconfig

print_hr "hostname"
hostname

print_hr "netstat"
netstat -n -l --inet

print_hr "top"
top -n 1

print_hr "ps"
ps aux 

print_hr "df"
df -h 

print_hr "free"
free -m

print_hr "arch"
arch

print_hr "lscpu"
lscpu

print_hr "uptime"
uptime

print_hr "EOF"
date

