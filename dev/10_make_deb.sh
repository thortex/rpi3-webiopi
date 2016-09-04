#!/bin/sh -x
# This file is based on 'make_deb' file in RPi.GPIO by Ben Croston
# Please refer to https://pypi.python.org/pypi/RPi.GPIO for more details.
ORIG_NAME=WebIOPi
NAME=webiopi
VERSION=0.7.1
if [ "$1" != "" ] ; then
    DISTRO="$1";
else
    DISTRO=`lsb_release -sc`;
fi
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
WORKDIR=~/build.${NAME}
set -e

cd ../${NAME}_${VERSION}/python
rm -fr ./WebIOPi.egg-info  
python setup.py sdist

rm -rf ${WORKDIR}
mkdir ${WORKDIR}

cd ..

cp ./python/dist/${ORIG_NAME}-${VERSION}.tar.gz \
    ${WORKDIR}/${NAME}_${VERSION}.orig.tar.gz

cd ${WORKDIR}
tar xvfz ${NAME}_${VERSION}.orig.tar.gz
cp -a ${SCRIPTPATH}/debian_${DISTRO} ${WORKDIR}/${ORIG_NAME}-${VERSION}/debian
mkdir -p ${WORKDIR}/doc
cp ${SCRIPTPATH}/../${NAME}_${VERSION}/doc/README ${WORKDIR}/doc

## build .deb files
cd ${WORKDIR}/${ORIG_NAME}-$VERSION
debuild -us -uc
##debuild clean

#cp ~/build_rpi.gpio/python*deb $SCRIPTPATH/dist
#cp ~/build_rpi.gpio/rpi.gpio_$VERSION~$DISTRO.orig.tar.gz $SCRIPTPATH/dist
#cp ~/build_rpi.gpio/rpi.gpio_$VERSION~$DISTRO*.dsc $SCRIPTPATH/dist
#cp ~/build_rpi.gpio/rpi.gpio_$VERSION~$DISTRO*.debian.tar.* $SCRIPTPATH/dist
#rm -rf ~/build_rpi.gpio
#rm $SCRIPTPATH/MANIFEST
