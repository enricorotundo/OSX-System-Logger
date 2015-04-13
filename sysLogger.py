#!/usr/bin/python

import time
import re
import time
import getpass
import copy
import psutil
import base64
import csv
from utils import executeBashCmd, cmdPiped
from collections import Counter

def grepBatteryCmd(text):
	pattern = re.compile('\d{1,3}')
	matches = re.findall(pattern, text)
	return str(matches[0])

def smcParser(text):
	lines = text.splitlines();
	smcData = {}
	for line in lines:
		smcData[line[2:6].strip()] = [line [8:14][1:-1].strip(), line [16:].split()[0]]
	return smcData

def getTimeStamp():
	data = {}
	data["timestamp"] = time.strftime("%a %b %d %X %Z %Y")
	return data

def getBatteryCharge():
	data = {}
	data["batteryValue"] = grepBatteryCmd(executeBashCmd("./bins/battery -pta"))
	return data

def getSMCregister(registerName, smcData):
	if smcData.has_key(registerName):
		return smcData[registerName][1]
	else:
		return "-99999" #i.e. error

def getSMCData():
	data = {}
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
	data = {}
	# USB PLUGGED DEVICES (even if not mounted like iPhones) 
	IOREGoutput = cmdPiped(cmdIOREG)
	pluggedDevices = set()
	lines = IOREGoutput.splitlines()
	usbDevices = ""
	for line in lines:
		pluggedDevices.update([line])
	if pluggedDevices != previousDevices:
		"#".join(str(device) for device in pluggedDevices)
		previousDevices = copy.deepcopy(pluggedDevices)
	devicesList = list(pluggedDevices)
	usbDevices = base64.b64encode(str(devicesList))
	data["usbDevices"] = usbDevices
	return data

def getPsutils():
	data = {}
	# CPU
	data["cpuPercentage"] = psutil.cpu_percent(interval=None)

	# VIRTUAL MEMORY
	data["memPercentage"] = psutil.virtual_memory().percent
	data["memAvailable"] = psutil.virtual_memory().available/1024
	data["memUsed"] = psutil.virtual_memory().used/1024
	data["memFree"] = psutil.virtual_memory().free/1024
	
	# SWAP MEMORY
	data["memSwapPercentage"] = psutil.swap_memory().percent
	data["memSwapUsed"] = psutil.swap_memory().used/1024
	data["memSwapFree"] = psutil.swap_memory().free/1024

	# DISKS COUNTERS
	data["diskReads"] = psutil.disk_io_counters().read_count
	data["diskWrite"] = psutil.disk_io_counters().write_count
	data["diskReadsMBytes"] = psutil.disk_io_counters().read_bytes/1024
	data["diskWriteMBytes"] = psutil.disk_io_counters().write_bytes/1024

	# NETWORK COUNTERS
	data["sentMBytes"] = psutil.net_io_counters(pernic=False).bytes_sent/1024
	data["recvMBytes"] = psutil.net_io_counters(pernic=False).bytes_recv/1024
	data["sentPackets"] = psutil.net_io_counters(pernic=False).packets_sent
	data["recvPackets"] = psutil.net_io_counters(pernic=False).packets_recv

	# PROCESSES	(FIRST 10, SORTED BY CPU USAGE)
	pList = []
	for proc in psutil.process_iter():
	    try:
	        pinfo = proc.as_dict(attrs=['name','cpu_percent'])	        
	    	if pinfo["cpu_percent"] > 0:
	    		pList.append(pinfo)
	    except psutil.NoSuchProcess:
	        pass
	sortedList = sorted(pList, key=lambda k: k['cpu_percent'], reverse=True)[0:10]
	encoded = ""
	if len(sortedList) > 0:
		encoded = base64.b64encode(str(sortedList))
	
	data["topProcesses"] = encoded
	return data


def gotoSleep(start_time, delay):
	# print str((time.time() - start_time)) + "\t" + str(delay - (time.time() - start_time))
	delta = delay - (time.time() - start_time)
	if delta > 0:
		time.sleep(delta)
	return

def main():
	delay=1;
	file = "logs/" + getpass.getuser() + "_log.csv"
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
		start_time = time.time() # MUST BE FIRST INSTRUCTION
		data = {}

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
		print data.keys()
		
		
		# # CREATE RECORD
		# record = time.strftime("%a %b %d %X %Z %Y") + "," + batteryValue + "," + fanSpeed + "," + cpuProximtyTemp +  "," + cpuACore1Temp +  "," + cpuACore2Temp + "," + cpuBCore1Temp +  "," + cpuBCore2Temp + "," + str(memPercentage) + "," + str(memAvailable) + "," + str(memUsed) + "," + str(memFree) + "," + str(cpuPercentage)
		# # print record
		# out_file.write(record + "\n")


		# with open(file,"a", 0) as csvfile:
		#     fieldnames = ['timestamp', 'batteryValue']
		#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		#     writer.writeheader()
		#     writer.writerow(data)


		gotoSleep(start_time, delay) # MUST BE LAST INSTRUCTION


if __name__ == '__main__':
	main()