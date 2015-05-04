#!/usr/bin/python

import time
import re
import time
import getpass
import copy
import csv
import os
import datetime
import psutil
from utils import executeBashCmd, executeBashCmdNoErr, cmdPiped
from collections import OrderedDict
from sys import platform as _platform
import subprocess

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
	data["datetime"] = ""
	data["timeFromEpoch"] = ""
	try:
		data["datetime"] = datetime.datetime.now().replace(microsecond=0).isoformat() # ISO 8601 Time Representation
		data["timeFromEpoch"] = time.time()
	except:
		pass
	return data

def getBatteryCharge():
	data = OrderedDict()
	try:
		if osName == 'darwin':
			# Mac OSX
			data["batteryValue"] = grepBatteryCmd(executeBashCmd("./bins/battery -pta"))
		else:
			# Linux
			text = executeBashCmd("acpi -b").split()[3].replace('%','')
			data["batteryValue"] = text
	except:
		data["batteryValue"] = -1
	return data

def getScreenBrightness():
	data = OrderedDict()
	try:
		if osName == 'darwin':
			# Mac
			text = executeBashCmdNoErr("./bins/screenbrightness -l")
			text = text.split('\n')[1].split()
			text = text[len(text) - 1]
			value = float(text)
			if float(0) <= float(value) <= float(1):
				data["screenbrightness"] = float(value)*100
			else:
				data["screenbrightness"] = -1
		else:
			# Linux
			text = executeBashCmdNoErr("xbacklight -get")
			data["screenbrightness"] = float(text)
	except:
		data["screenbrightness"] = -1


	return data

def getSMCregister(registerName, smcData):
	if smcData.has_key(registerName):
		return smcData[registerName][1]
	else:
		return -1

def getSMCData():
	data = OrderedDict()
	if osName == 'darwin':
		# Mac OSX
		smcData = smcParser(executeBashCmd("./bins/smc -l"))
		# SMC registers: https://github.com/jedda/OSX-Monitoring-Tools/blob/master/check_osx_smc/known-registers.md		
		data["fanSpeed"] = getSMCregister('F0Ac', smcData)
		data["cpuProximtyTemp"] = getSMCregister('TC0P', smcData)
		data["cpuACore1Temp"] = getSMCregister('TC0C', smcData)
		data["cpuACore2Temp"] = getSMCregister('TC1C', smcData)
		data["cpuBCore1Temp"] = getSMCregister('TC2C', smcData)
		data["cpuBCore2Temp"] = getSMCregister('TC3C', smcData)
	else:
		# Linux
		try:
			Thermal 0: ok, 54.0 degrees C
			Thermal 1: ok, 51.0 degrees C

			text = executeBashCmd("acpi -t").splitlines()
			temps = [-1, -1]
			for i, line in enumerate(text):
				temps[i] = line.split()[3]
			
			data["fanSpeed"] = -1
			data["cpuProximtyTemp"] = -1
			data["cpuACore1Temp"] = temps[0]
			data["cpuACore2Temp"] = -1
			data["cpuBCore1Temp"] = temps[1]
			data["cpuBCore2Temp"] = -1
		except:
			data["fanSpeed"] = -1
			data["cpuProximtyTemp"] = -1
			data["cpuACore1Temp"] = -1
			data["cpuACore2Temp"] = -1
			data["cpuBCore1Temp"] = -1
			data["cpuBCore2Temp"] = -1
	return data



def getUsbPluggedDevs(cmdIOREG, previousDevices):
	data = OrderedDict()
	# USB PLUGGED DEVICES (even if not mounted like iPhones) 
	if osName == 'darwin':
		# Mac OSX
		pluggedDevices = set()
		IOREGoutput = cmdPiped(cmdIOREG)
		lines = IOREGoutput.splitlines()
		for line in lines:
			pluggedDevices.update([line])
		if pluggedDevices != previousDevices:
			"#".join(str(device) for device in pluggedDevices)
			previousDevices = copy.deepcopy(pluggedDevices)
		devicesList = list(pluggedDevices)
		data["usbDevices"] = str(devicesList) # List of Strings, example: ['Storage Media', 'iPhone']
	else:
		# Linux
		device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
		df = subprocess.check_output("lsusb", shell=True)
		devices = []
		for i in df.split('\n'):
		    if i:
		        info = device_re.match(i)
		        if info:
		            dinfo = info.groupdict()
		            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
		            devices.append(dinfo)
	    list = []
	    for i in devices:
	    	list.append(i['tag'])
	    # devices:
	    # [
		# {'device': '/dev/bus/usb/001/009', 'tag': 'Apple, Inc. Optical USB Mouse [Mitsumi]', 'id': '05ac:0304'},
		# {'device': '/dev/bus/usb/001/001', 'tag': 'Linux Foundation 2.0 root hub', 'id': '1d6b:0002'},
		# {'device': '/dev/bus/usb/001/002', 'tag': 'Intel Corp. Integrated Rate Matching Hub', 'id': '8087:0020'},
		# {'device': '/dev/bus/usb/001/004', 'tag': 'Microdia ', 'id': '0c45:641d'}
		# ]
		data["usbDevices"] = str(list)
	return data

def getPsutils():
	data = OrderedDict()
	
	# CPU
	try:
		data["cpuPercentage"] = psutil.cpu_percent(interval=None, percpu=True)
	except psutil.Error:
		data["cpuPercentage"] = []
	
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
	data["topProcesses"] = str(topProcesses) # List of Dicts
	
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

osName = ''

def main():
	
	try:
		# GET USERNAME
		username = "unknow_user"
		try:
			username = getpass.getuser()
		except:
			pass

		# GET OS NAME
		if _platform == "linux" or _platform == "linux2":
		    # linux
		    osName = 'linux'
		elif _platform == "darwin":
		    # OS X
		    osName = 'darwin'
		elif _platform == "win32":
		    # Windows...
		    osName = 'win32'

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

				if data["datetime"] != "":
					# USERNAME
					data["username"] = username
					# BATTERY [Mac + Linux]
					data.update(getBatteryCharge())
					# SMC: Fan speed + Temperatures [Mac OSX + Linux]
					data.update(getSMCData())
					# USB DEVS [Mac OSX + Linux]
					data.update(getUsbPluggedDevs(cmdIOREG, previousDevices))
					# PSUTIL: cpu, ram, io, processes
					data.update(getPsutils())
					# screen Bright [Mac OSX Only]
					data.update(getScreenBrightness())
				
				# WRITE CSV
				delta = delay - (time.time() - start_time)
				if len(data) == 29 and delta > 0: # write only if all data have been collected and check if the mac has slept (delta < 0)
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