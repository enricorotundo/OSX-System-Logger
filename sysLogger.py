#!/usr/bin/python

import time
import re
import time
import getpass
import copy
import base64
import csv
import os
import datetime
import psutil
from utils import executeBashCmd, cmdPiped
from collections import OrderedDict

def grepBatteryCmd(text):
	pattern = re.compile('\d{1,3}')
	matches = re.findall(pattern, text)
	return str(matches[0])

def smcParser(text):
	lines = text.splitlines();
	smcData = OrderedDict()
	for line in lines:
		smcData[line[2:6].strip()] = [line [8:14][1:-1].strip(), line [16:].split()[0]]
	return smcData

def getTimeStamp():
	data = OrderedDict()
	data["timestamp"] = datetime.datetime.now().replace(microsecond=0).isoformat() # ISO 8601 Time Representation
	return data

def getBatteryCharge():
	data = OrderedDict()
	data["batteryValue"] = grepBatteryCmd(executeBashCmd("./bins/battery -pta"))
	return data

def getSMCregister(registerName, smcData):
	if smcData.has_key(registerName):
		return smcData[registerName][1]
	else:
		return "" #i.e. error

def getSMCData():
	data = OrderedDict()
	smcData = smcParser(executeBashCmd("./bins/smc -l"))
	# SMC registers: https://github.com/jedda/OSX-Monitoring-Tools/blob/master/check_osx_smc/known-registers.md		
	data["fanSpeed"] = getSMCregister('F0Ac', smcData)
	data["cpuProximtyTemp"] = getSMCregister('TC0P', smcData)
	data["cpuACore1Temp"] = getSMCregister('TC0C', smcData)
	data["cpuACore2Temp"] = getSMCregister('TC1C', smcData)
	data["cpuBCore1Temp"] = getSMCregister('TC2C', smcData)
	data["cpuBCore2Temp"] = getSMCregister('TC3C', smcData)
	return data

def getUsbPluggedDevs(cmdIOREG, previousDevices):
	data = OrderedDict()
	# USB PLUGGED DEVICES (even if not mounted like iPhones) 
	IOREGoutput = cmdPiped(cmdIOREG)
	pluggedDevices = set()
	lines = IOREGoutput.splitlines()
	for line in lines:
		pluggedDevices.update([line])
	if pluggedDevices != previousDevices:
		"#".join(str(device) for device in pluggedDevices)
		previousDevices = copy.deepcopy(pluggedDevices)
	devicesList = list(pluggedDevices)
	data["usbDevices"] = base64.b64encode(str(devicesList)) # base64 of a List of Strings, example: ['Storage Media', 'iPhone']
	return data

def getPsutils():
	data = OrderedDict()
	# CPU
	data["cpuPercentage"] = psutil.cpu_percent(interval=None)
	# VIRTUAL MEMORY
	data["memPercentage"] = psutil.virtual_memory().percent
	data["memAvailable"] = psutil.virtual_memory().available
	data["memUsed"] = psutil.virtual_memory().used
	data["memFree"] = psutil.virtual_memory().free
	# SWAP MEMORY
	data["memSwapPercentage"] = psutil.swap_memory().percent
	data["memSwapUsed"] = psutil.swap_memory().used
	data["memSwapFree"] = psutil.swap_memory().free
	# DISKS COUNTERS
	data["diskReads"] = psutil.disk_io_counters().read_count
	data["diskWrite"] = psutil.disk_io_counters().write_count
	data["diskReadsBytes"] = psutil.disk_io_counters().read_bytes
	data["diskWriteBytes"] = psutil.disk_io_counters().write_bytes
	# NETWORK COUNTERS
	data["sentBytes"] = psutil.net_io_counters(pernic=False).bytes_sent
	data["recvBytes"] = psutil.net_io_counters(pernic=False).bytes_recv
	data["sentPackets"] = psutil.net_io_counters(pernic=False).packets_sent
	data["recvPackets"] = psutil.net_io_counters(pernic=False).packets_recv
	# PROCESSES
	processesList = [] # List of Dicts, example: [{'name': 'loginwindow', 'cpu_percent': 0.1}, ...]
	for proc in psutil.process_iter():
	    try:
	        pinfo = proc.as_dict(attrs=['name','cpu_percent'])	        
	    	if pinfo["cpu_percent"] > 0:
	    		processesList.append(pinfo)
	    except psutil.NoSuchProcess:
	        pass
	data["topProcesses"] = base64.b64encode(str(processesList)) # base64 representation of a List of Dicts
	
	return data


def gotoSleep(start_time, delay):
	# print str((time.time() - start_time)) + "\t" + str(delay - (time.time() - start_time))
	delta = delay - (time.time() - start_time)
	if delta > 0:
		time.sleep(delta)
	return

def writeCSV(data, fieldnames):
	file = "logs/" + getpass.getuser() + "_log.csv"
	file_exists = os.path.isfile(file)
	with open(file,"a", 0) as csvfile:
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		    if not file_exists:
        		writer.writeheader()  # file doesn't exist yet, write a header
		    writer.writerow(data)
	return

def main():
	delay=1;
	config_path="usbDevices_config.txt"

	# GETTING DEFAULT USB DEVICES
	defaultUSB = set()
	config_file = open(config_path,"r")
	for line in config_file.readlines():
		key = line.replace('\n','')
		if key not in defaultUSB:
			defaultUSB.add(key)
	config_file.close()
	# # CREATING IOREG CMD
	cmdIOREG="grep -i -v '^Root.*"
	for value in defaultUSB:
		cmdIOREG = cmdIOREG + "\|^" + value
	cmdIOREG = cmdIOREG + "'"
	previousDevices = set()

	# INIT
	foo = psutil.cpu_percent(interval=None)

	while True:
		# START LOOP
		start_time = time.time() # MUST BE FIRST INSTRUCTION
		
		data = OrderedDict()
		# TIMESTAMP
		data.update(getTimeStamp())
		# BATTERY [Mac OSX Only]
		data.update(getBatteryCharge())
		# SMC: Fan speed + Temperatures [Mac OSX Only]
		data.update(getSMCData())
		# USB DEVS [Mac OSX Only]
		data.update(getUsbPluggedDevs(cmdIOREG, previousDevices))
		# PSUTIL: cpu, ram, io, processes
		data.update(getPsutils())
		# print data
	
		writeCSV(data, data.keys())
		# END LOOP
		gotoSleep(start_time, delay) # MUST BE LAST INSTRUCTION


if __name__ == '__main__':
	main()