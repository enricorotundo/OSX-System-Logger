#!/usr/bin/python

# NOTE: this script requires SUDO

import time
import getpass
from utils import executeBashCmd

ntpServer = "ntp1.inrim.it"
ntpLogFile = "logs/" + getpass.getuser() + "_ntpd_update.txt"
ntpCmd="ntpd -q"
configCmd="cat /etc/ntp.conf"
checkCmd = "systemsetup -getusingnetworktime"
setNtpCmd = "systemsetup -setnetworktimeserver " + ntpServer

try:
	executeBashCmd("systemsetup -setusingnetworktime off")
	ntpCmdOut = executeBashCmd(ntpCmd)
	ntpConfigOut = executeBashCmd(configCmd)
	checkCmdOut = executeBashCmd(checkCmd)
	setNtpCmdOut = executeBashCmd(setNtpCmd)
	record = executeBashCmd("date").rstrip('\n') + "\t" + setNtpCmdOut.rstrip('\n') + "\t" + checkCmdOut.rstrip('\n') + "\t" + ntpConfigOut.rstrip('\n') + "\t" + ntpCmdOut
	out_file = open(ntpLogFile,"a", 0)
	out_file.write(record + "\n")
	out_file.close()
	time.sleep(12)
except:
	pass
