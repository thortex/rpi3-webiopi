#!/bin/sh -x

x=`cat /etc/os-release | grep stretch`
if [ "x$x" != "x" ] ; then
   extras=""   
else
   extras="hardening-includes"
fi


sudo apt-get install \
 build-essential dh-make fakeroot devscripts pbuilder cdbs \
 at autotools-dev cdbs dctrl-tools debian-keyring debootstrap \
 devscripts dh-make diffstat distro-info-data dput equivs \
 exim4-base exim4-config exim4-daemon-light \
 libapt-pkg-perl libarchive-zip-perl libclass-accessor-perl \
 libclass-inspector-perl libclone-perl libcommon-sense-perl \
 libconvert-binhex-perl libcrypt-ssleay-perl libdigest-hmac-perl \
 libdistro-info-perl libemail-valid-perl libencode-locale-perl \
 libexporter-lite-perl libfcgi-perl libfile-listing-perl \
 libfont-afm-perl libhtml-form-perl libhtml-format-perl \
 libhtml-parser-perl libhtml-tagset-perl libhtml-tree-perl \
 libhttp-cookies-perl libhttp-daemon-perl libhttp-date-perl \
 libhttp-message-perl libhttp-negotiate-perl libio-pty-perl \
 libio-socket-ip-perl libio-socket-ssl-perl libio-string-perl \
 libio-stringy-perl libipc-run-perl libjson-perl libjson-xs-perl \
 liblwp-mediatypes-perl liblwp-protocol-https-perl libmailtools-perl \
 libmime-tools-perl libnet-dns-perl libnet-domain-tld-perl \
 libnet-http-perl libnet-ip-perl libnet-ssleay-perl libossp-uuid-perl \
 libossp-uuid16 libparse-debcontrol-perl libparse-debianchangelog-perl \
 libsoap-lite-perl libsocket-perl libsub-name-perl libtask-weaken-perl \
 libtie-ixhash-perl liburi-perl libwww-perl libwww-robotrules-perl \
 libxml-namespacesupport-perl libxml-parser-perl libxml-sax-base-perl \
 libxml-sax-expat-perl libxml-sax-perl libxml-simple-perl lintian \
 lsb-release patchutils pbuilder python-apt python-apt-common \
 python-chardet python-debian python-magic wdiff ${extras}
