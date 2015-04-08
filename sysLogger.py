#!/usr/bin/python

import time
import re
import time
import getpass
import copy
from utils import executeBashCmd, cmdPiped

delay=1;
usbLogFile = "logs/" + getpass.getuser() + "_USB_log.csv"
file = "logs/" + getpass.getuser() + "_log.csv"
batteryCmd = "./bins/battery -pt" # get battery percentage
smcCmd = "./bins/smc -l" # get SMC data
config_path="usbDevices_config.txt"

def grepBatteryCmd(text):
	pattern = re.compile('\d{1,3}')
	matches = re.findall(pattern, text)
	return matches[0]

def smcParser(text):
	lines = text.splitlines();
	smcData = {}
	for line in lines:
		smcData[line[2:6].strip()] = [line [8:14][1:-1].strip(), line [16:].split()[0]]
	return smcData

def getSMCregister(registerName, smcData):
	if smcData.has_key(registerName):
		return smcData[registerName][1]
	else:
		return "-99999" #i.e. error

def vmstatParser(text):
	pagesData = {}
	memData = {}
	for line in text.replace('.', '').splitlines()[1:]:
		data = line.replace(' ', '').split(':')
		pagesData[data[0]] = data[1]
	memData['WiredMem'] = str((int(pagesData['Pageswireddown'])*4096)/1024/1024)
	memData['ActiveMem'] = str((int(pagesData['Pagesactive'])*4096)/1024/1024)
	memData['InactiveMem'] = str((int(pagesData['Pagesinactive'])*4096)/1024/1024)
	memData['FreeMem'] = str((int(pagesData['Pagesfree'])*4096)/1024/1024)
	return memData


# GETTING DEFAULT USB DEVICES
defaultUSB = set()
config_file = open(config_path,"r")
for line in config_file.readlines():
	key = line.replace('\n','')
	if key not in defaultUSB:
		defaultUSB.add(key)
config_file.close()

# CREATING IOREG CMD
cmdIOREG="grep -i -v '^Root.*"
for value in defaultUSB:
	cmdIOREG = cmdIOREG + "\|^" + value
cmdIOREG = cmdIOREG + "'"
previousDevices = set()


out_file = open(file,"a", 0)
usb_log_file = open(usbLogFile,"a", 0)

while True:
	start_time = time.time()
	
	# USB PLUGGED DEVICES (even if not mounted like iPhones) 
	IOREGoutput = cmdPiped(cmdIOREG)
	pluggedDevices = set()
	lines = IOREGoutput.splitlines()
	for line in lines:
		pluggedDevices.update([line])
	if pluggedDevices != previousDevices:
		record = time.strftime("%a %b %d %X %Z %Y")
		for device in pluggedDevices:
			record = record + "," + device
		usb_log_file.write(record + "\n")
		previousDevices = copy.deepcopy(pluggedDevices)
	
	# BATTERY, FAN, TEMPERATURES
	data = {}
	batteryValue = grepBatteryCmd(executeBashCmd(batteryCmd))
	smcData = smcParser(executeBashCmd(smcCmd))
	memData = vmstatParser(executeBashCmd("vm_stat"))
	# SMC registers: https://github.com/jedda/OSX-Monitoring-Tools/blob/master/check_osx_smc/known-registers.md		
	fanSpeed = getSMCregister('F0Ac', smcData)
	cpuProximtyTemp = getSMCregister('TC0P', smcData)
	cpuACore1Temp = getSMCregister('TC0C', smcData)
	cpuACore2Temp = getSMCregister('TC1C', smcData)
	cpuBCore1Temp = getSMCregister('TC2C', smcData)
	cpuBCore2Temp = getSMCregister('TC3C', smcData)
	record = time.strftime("%a %b %d %X %Z %Y") + "," + batteryValue + "," + fanSpeed + "," + cpuProximtyTemp +  "," + cpuACore1Temp +  "," + cpuACore2Temp + "," + cpuBCore1Temp +  "," + cpuBCore2Temp + "," + memData['WiredMem'] + "," + memData['ActiveMem'] + "," + memData['InactiveMem'] + "," + memData['FreeMem']
	out_file.write(record + "\n")


	# print str((time.time() - start_time)) + "\t" + str(delay - (time.time() - start_time))
	time.sleep(delay - (time.time() - start_time))
