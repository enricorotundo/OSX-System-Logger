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

	
1. Create launchd plist file from template (it must not be writable by anyone other than the owner)
	
	```
	cp launchd_config/com.apple.energyprofiler.cpuLogger.plist.template launchd_config/com.apple.energyprofiler.cpuLogger.plist
	cp launchd_config/com.apple.energyprofiler.lastDump.plist.template launchd_config/com.apple.energyprofiler.lastDump.plist
	cp launchd_config/com.apple.energyprofiler.ntpUpdater.plist.template launchd_config/com.apple.energyprofiler.ntpUpdater.plist
	cp launchd_config/com.apple.energyprofiler.sysLogger.plist.template launchd_config/com.apple.energyprofiler.sysLogger.plist
	```

1. Change ```ntpUpdater.plist``` owner:

	```
	sudo chown root /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.ntpUpdater.plist
	```

1. Run this, it will copy the current absolute path in your clipboard (usefull for the next step)

	```
	pwd | pbcopy
	```		
		
1. Modify every ```launchd_config/com.apple.energyprofiler.*.plist``` replacing **every** occurrences of the (entire) string ```/Users/erotundo/git/OSX-System-Logger/``` with your local repository absolute path (obtained in previous the step).

1. Create launchd symlink
	
	```
	ln -s /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.cpuLogger.plist ~/Library/LaunchAgents/com.apple.energyprofiler.cpuLogger.plist
	ln -s /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.lastDump.plist ~/Library/LaunchAgents/com.apple.energyprofiler.lastDump.plist
	ln -s /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.sysLogger.plist ~/Library/LaunchAgents/com.apple.energyprofiler.sysLogger.plist
	```
1. Sudo
	```
	sudo ln -s /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.ntpUpdater.plist /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist
	```

1. Logout and login back
	
1. To Check if scripts are working, run the following commands:
	
	```
	sudo launchctl list | grep energyprofiler
	```

	should show:

	```
	-	0	com.apple.energyprofiler.ntpUpdater
	```

	and

	```
	launchctl list | grep energyprofiler
	```

	should show:

	```
	2475	0	com.apple.energyprofiler.sysLogger
	2462	0	com.apple.energyprofiler.cpuLogger
	-		0	com.apple.energyprofiler.lastDump
	```

	Furthermore, you can ```tail -f``` all the files in the ```logs/``` directory.
	

	NOTE: 

	1. if the second column reports not-zero means that and error occurred in the script execution
	1. first column is the PID of the running script (useful to monitor or kill the process)
	
	
### Uninstall

1. 
```
sudo rm /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist
rm ~/Library/LaunchAgents/com.apple.energyprofiler.*
```

1. Goto ```System Preferences -> Date & Time``` and enable ```Set date and time automatically```, then choose an NTP server