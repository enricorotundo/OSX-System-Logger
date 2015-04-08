# OSX System Logger

### Requirements:

* Command line tools installed (xcode)
* Python 2.7 
* *sudo* permissions


### Install (Mac OSX 10.10.2):

1. Clone the repo:

	```
	git clone https://github.com/tundo91/OSX-System-Logger.git
	```
	
1. Enter the folder:

	```
	cd	OSX-System-Logger
	```

1. Run:

	```
	ioreg -p IOUSB -w0 | sed 's/[^o]*o //; s/@.*$//' | grep -i -v '^Root.*' > usbDevices_config.txt
	```

1. Change folder

	```
	cd launchd_config/
	```
	
1. Create launchd plist files from template (they must not be writable by anyone other than the owner!)
	
	```
	cp com.apple.energyprofiler.cpuLogger.plist.template com.apple.energyprofiler.cpuLogger.plist
	cp com.apple.energyprofiler.lastDump.plist.template com.apple.energyprofiler.lastDump.plist
	cp com.apple.energyprofiler.ntpUpdater.plist.template com.apple.energyprofiler.ntpUpdater.plist
	cp com.apple.energyprofiler.sysLogger.plist.template com.apple.energyprofiler.sysLogger.plist
	```

1. Change ```ntpUpdater.plist``` owner: 

	```
	sudo chown root com.apple.energyprofiler.ntpUpdater.plist
	```

1. Copy the current absolute path in your clipboard (usefull for the next step)

	```
	pwd | pbcopy
	```
	NOTE: in the following steps the absolute path is referred as ```{LOCAL_ABS_PATH}```

		
1. Modify every ```.plist``` file replacing **every** occurrences of the (entire) string: 
	
	```
	/Users/erotundo/git/OSX-System-Logger/
	``` 
	
	with your local repository absolute path, obtained in previous step.

1. Create user's launchd symlinks (important: use the absolute path)
	
	```
	ln -s {LOCAL_ABS_PATH}/launchd_config/com.apple.energyprofiler.cpuLogger.plist ~/Library/LaunchAgents/com.apple.energyprofiler.cpuLogger.plist
	ln -s {LOCAL_ABS_PATH}/launchd_config/com.apple.energyprofiler.lastDump.plist ~/Library/LaunchAgents/com.apple.energyprofiler.lastDump.plist
	ln -s {LOCAL_ABS_PATH}/launchd_config/com.apple.energyprofiler.sysLogger.plist ~/Library/LaunchAgents/com.apple.energyprofiler.sysLogger.plist
	```

1. Create root's launchd symlinks (important: use the absolute path)

	```
	sudo ln -s {LOCAL_ABS_PATH}/launchd_config/com.apple.energyprofiler.ntpUpdater.plist /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist
	```

1. **LOGOUT**

1. Login *(this script assumes that you always use the same system user)*
	
1. Check if scripts are actually working, run the following commands:
	
	```
	sudo launchctl list | grep energyprofiler
	```

	should show something similar to:

	```
	-	0	com.apple.energyprofiler.ntpUpdater
	```

	...and...

	```
	launchctl list | grep energyprofiler
	```

	should show something similar to:

	```
	2475	0	com.apple.energyprofiler.sysLogger
	2462	0	com.apple.energyprofiler.cpuLogger
	-		0	com.apple.energyprofiler.lastDump
	```

	Furthermore, you can ```tail -f``` all the files in the ```logs/``` directory.
	

	NOTE: 

	1. If the second column reports not-zero means that and error occurred in the script execution
	1. First column is the PID of the running script (useful to monitor or kill the process)
	
	
### Uninstall

1. Remove launchd configurations
```
sudo rm /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist
rm ~/Library/LaunchAgents/com.apple.energyprofiler.*
```

1. Goto ```System Preferences``` pane, then select ```Date & Time``` and enable ```Set date and time automatically```, choose a preferred Apple NTP server from the dropdown list.

### For questions refer to:
Enrico Rotundo <enrico.rotundo@gmail.com>
