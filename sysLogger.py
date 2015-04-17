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

def getISODateTime():
	data = OrderedDict()
	data["datetimeISO"] = ""
	try:
		data["datetimeISO"] = datetime.datetime.now().replace(microsecond=0).isoformat() # ISO 8601 Time Representation
	except:
		pass
	return data

def getBatteryCharge():
	data = OrderedDict()
	try:
		data["batteryValue"] = grepBatteryCmd(executeBashCmd("./bins/battery -pta"))
	except:
		data["batteryValue"] = -1
	return data

def getSMCregister(registerName, smcData):
	if smcData.has_key(registerName):
		return smcData[registerName][1]
	else:
		return -1

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
	try:
		data["cpuPercentage"] = psutil.cpu_percent(interval=None)
	except psutil.Error:
		data["cpuPercentage"] = -1
	
	# VIRTUAL MEMORY
	try:
		data["memPercentage"] = psutil.virtual_memory().percent
	except psutil.Error:
		data["memPercentage"] = -1
	try:
		data["memAvailable"] = psutil.virtual_memory().available
	except psutil.Error:
		data["memAvailable"] = -1
	try:
		data["memUsed"] = psutil.virtual_memory().used
	except psutil.Error:
		data["memUsed"] = -1
	try:
		data["memFree"] = psutil.virtual_memory().free
	except psutil.Error:
		data["memFree"] = -1

	
	# SWAP MEMORY
	try:
		data["memSwapPercentage"] = psutil.swap_memory().percent
	except psutil.Error:
		data["memSwapPercentage"] = -1
	try:
		data["memSwapUsed"] = psutil.swap_memory().used
	except psutil.Error:
		data["memSwapUsed"] = -1
	try:
		data["memSwapFree"] = psutil.swap_memory().free
	except psutil.Error:
		data["memSwapFree"] = -1
	
	# DISKS COUNTERS
	try:
		data["diskReads"] = psutil.disk_io_counters().read_count
	except psutil.Error:
		data["diskReads"] = -1
	try:
		data["diskWrite"] = psutil.disk_io_counters().write_count
	except psutil.Error:
		data["diskWrite"] = -1
	try:
		data["diskReadsBytes"] = psutil.disk_io_counters().read_bytes
	except psutil.Error:
		data["diskReadsBytes"] = -1
	try:
		data["diskWriteBytes"] = psutil.disk_io_counters().write_bytes
	except psutil.Error:
		data["diskWriteBytes"] = -1

	# NETWORK COUNTERS
	try:
		data["sentBytes"] = psutil.net_io_counters(pernic=False).bytes_sent
	except psutil.Error:
		data["sentBytes"] = -1
	try:
		data["recvBytes"] = psutil.net_io_counters(pernic=False).bytes_recv
	except psutil.Error:
		data["recvBytes"] = -1
	try:
		data["sentPackets"] = psutil.net_io_counters(pernic=False).packets_sent
	except psutil.Error:
		data["sentPackets"] = -1
	try:
		data["recvPackets"] = psutil.net_io_counters(pernic=False).packets_recv
	except psutil.Error:
		data["recvPackets"] = -1
		
	# PROCESSES
	topProcesses = [] # List of Dicts, example: [{'name': 'loginwindow', 'cpu_percent': 0.1}, ...]
	for proc in psutil.process_iter():
	    try:
	        pinfo = proc.as_dict(attrs=['name','cpu_percent'])	        
	    	if pinfo["cpu_percent"] > 0:
	    		topProcesses.append(pinfo)
	    except psutil.NoSuchProcess:
	        pass
	data["topProcesses"] = base64.b64encode(str(topProcesses)) # base64 representation of a List of Dicts
	
	return data

def writeCSV(data, fieldnames):
	try:
		file = "logs/" + getpass.getuser() + "_log_" + time.strftime("%m%d%Y") + ".csv"
		file_exists = os.path.isfile(file)
		with open(file,"a", 0) as csvfile:
			    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			    if not file_exists:
	        		writer.writeheader()  # file doesn't exist yet, write a header
			    writer.writerow(data)
	except:
		pass
	return

def main():
	
	try:
		# GET USERNAME
		username = "unknow_user"
		try:
			username = getpass.getuser()
		except:
			pass

		# GETTING DEFAULT USB DEVICES
		config_path="usbDevices_config.txt"
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
		delay=1;

		while True:
			try:
				# START LOOP
				start_time = time.time() # MUST BE FIRST INSTRUCTION
				
				data = OrderedDict()
				# TIMESTAMP
				data.update(getISODateTime())

				if data["datetimeISO"] != "":
					# USERNAME
					data["username"] = username
					# BATTERY [Mac OSX Only]
					data.update(getBatteryCharge())
					# SMC: Fan speed + Temperatures [Mac OSX Only]
					data.update(getSMCData())
					# USB DEVS [Mac OSX Only]
					data.update(getUsbPluggedDevs(cmdIOREG, previousDevices))
					# PSUTIL: cpu, ram, io, processes
					data.update(getPsutils())
				
				# WRITE CSV
				delta = delay - (time.time() - start_time)
				if len(data) == 27 and delta > 0: # write only if all data have been collected and check if the mac has slept (delta < 0)
					writeCSV(data, data.keys())
				else:
					continue
				
				# GOTO SLEEP
				delta = delay - (time.time() - start_time)
				if delta > 0:
					time.sleep(delta)
				else:
					continue
				# MUST BE LAST INSTRUCTION	
			except:
				time.sleep(1)
				pass
	except:
		pass


if __name__ == '__main__':
	main()