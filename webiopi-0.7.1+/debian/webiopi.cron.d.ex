#
# Regular cron jobs for the webiopi package
#
0 4	* * *	root	[ -x /usr/bin/webiopi_maintenance ] && /usr/bin/webiopi_maintenance
