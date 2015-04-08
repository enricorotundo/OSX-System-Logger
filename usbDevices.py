#!/usr/bin/python

import time
import sys
from utils import executeBashCmd



cmd="ioreg -p IOUSB -w0 | sed 's/[^o]*o //; s/@.*$//' | grep -i -v '^Root.*\|'"

config_path="usbDevices_config.txt"



try:
	defaultValues = []
	config_file = open(config_path,"r")
	for line in config_file.readlines():
		key = line.replace('\n','')
		if key not in defaultValues:
			defaultValues.append(key)
	config_file.close()
	print "The following are default IOUSB keys in this Mac:"
	print defaultValues

except:
    print "Unexpected error:", sys.exc_info()[0]