#
# Regular cron jobs for the attackfeed-1.0 package
#
0 4	* * *	root	[ -x /usr/bin/attackfeed-1.0_maintenance ] && /usr/bin/attackfeed-1.0_maintenance
