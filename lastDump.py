#!/usr/bin/python

import getpass
import time
from utils import executeBashCmd

loginCmd = "last" # get login history
lastLog = "logs/" + getpass.getuser() + "_last.txt"

def lastFileDump():
	last_file = open(lastLog,"a", 0)
	last_file.write(executeBashCmd("last"))
	last_file.close()
	return

lastFileDump()
time.sleep(12)