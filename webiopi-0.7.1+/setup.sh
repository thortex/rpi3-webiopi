#!/bin/sh
# WebIOPi setup script

SEARCH="python python3"
FOUND=""
INSTALLED=""

if [ "$#" = "1" ]; then
	command="$1"
else
	command="none"
fi

echo
echo "Installing WebIOPi..."
echo

if [ "$command" != "skip-apt" ]; then
	echo "Updating apt package list..."
	apt-get update
	echo
fi

# Install Python library
cd python

# Look up for installed python
for python in $SEARCH; do
	program="/usr/bin/$python"
	if [ -x $program ]; then
		FOUND="$FOUND $python"
		version=`$python -V 2>&1`
		include=`$python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())"`
		echo "Found $version... "

		if [ "$command" != "skip-apt" ]; then
			# Install required dev header and setuptools
			echo "Trying to install $python-dev using apt-get"
			apt-get install -y $python-dev $python-setuptools
		fi

		# Try to compile and install for the current python
		if [ -f "$include/Python.h" ]; then
			echo "Trying to install WebIOPi for $version"
			$python setup.py install
			if [ "$?" -ne "0" ]; then
				# Sub setup error, continue with next python
				echo "Build for $version failed\n"
				continue
			fi
			echo "WebIOPi installed for $version\n"
			INSTALLED="$INSTALLED $python"
		else
			echo "Cannot install for $version : missing development headers\n"
		fi
	fi
done

# Go back to the root folder
cd ..

# Ensure WebIOPi is installed to continue
if [ -z "$INSTALLED" ]; then
	if [ -z "$FOUND" ]; then
		echo "ERROR: WebIOPi cannot be installed - neither python or python3 found"
		exit 1
	else
		echo "ERROR: WebIOPi cannot be installed - please check errors above"
		exit 2
	fi
fi

# Select greater python version
for python in $INSTALLED; do
	echo $python > /dev/null
done

# Update HTML resources
echo "Copying HTML resources..."
mkdir /usr/share/webiopi 2>/dev/null 1>/dev/null
cp -rfv htdocs /usr/share/webiopi
echo

# Add config file if it does not exist
if [ ! -f "/etc/webiopi/config" ]; then
	echo "Copying default config file..."
	mkdir /etc/webiopi 2>/dev/null 1>/dev/null
	cp -v python/config /etc/webiopi/config
fi

# Add passwd file if it does not exist
if [ ! -f "/etc/webiopi/passwd" ]; then
	echo "Copying default passwd file..."
	mkdir /etc/webiopi 2>/dev/null 1>/dev/null
	cp -v python/passwd /etc/webiopi/passwd
fi

# Add service/daemon script
#if [ ! -f "/etc/init.d/webiopi" ]; then
echo "Installing startup script..."
cp -rf python/webiopi.init.sh /etc/init.d/webiopi
sed -i "s/python/$python/g" /etc/init.d/webiopi
chmod 0755 /etc/init.d/webiopi

# Add webiopi command
echo "Installing webiopi command..."
cp -rf python/webiopi.sh /usr/bin/webiopi
sed -i "s/python/$python/g" /usr/bin/webiopi
chmod 0755 /usr/bin/webiopi

# Add webiopi-passwd command
echo "Installing webiopi-passwd command..."
cp -rf python/webiopi-passwd.py /usr/bin/webiopi-passwd
sed -i "s/python/$python/g" /usr/bin/webiopi-passwd
chmod 0755 /usr/bin/webiopi-passwd

# Weaved installer
echo
echo "Do you want to access WebIOPi over Internet ? [y/n]"
read response
WEAVED=0
if [ "$response" = "y" ]; then
    ./weaved-setup.bin
    if [ "$?" = "0" ]; then
        WEAVED=1
    else
        WEAVED=2
    fi
    clear
fi
    

# Display WebIOPi usages
echo
echo "WebIOPi successfully installed"
echo "* To start WebIOPi foreground\t: sudo webiopi [-h] [-c config] [-l log] [-s script] [-d] [port]"
echo
echo "* To start WebIOPi background\t: sudo /etc/init.d/webiopi start"
echo "* To start WebIOPi at boot\t: sudo update-rc.d webiopi defaults"
echo

if [ "$WEAVED" = "0" ]; then
    echo "* Run ./weaved-setup.bin to install the Weaved IoT Kit and access your device over Internet"
elif [ "$WEAVED" = "1" ]; then
    echo "* Weaved IoT Kit installed, log on http://developer.weaved.com to access your device"
elif [ "$WEAVED" = "2" ]; then
    echo "! Something went wrong while installing the Weaved IoT Kit."
    echo "* Run ./weaved-setup.bin to restart the Weaved IoT Kit Installer."
fi
    
echo
echo "* Look in `pwd`/examples for Python library usage examples"
echo
