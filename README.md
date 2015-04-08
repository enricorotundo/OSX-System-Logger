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

1. Create the configuration file for the USB devices logger

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
1. Run this, it will copy the absolute path in your clipboard (usefull for the next step)

	```
	pwd | pbcopy
	```		
		
1. Modify the new ```launchd_config/com.apple.energyprofiler.plist``` replacing **every** occurences of the (entire) string ```/Users/erotundo/git/OSX-System-Logger/``` with your local repository absolute path (obtained in previous the step).

1. Create launchd symlink
	
	```
	ln -s /Users/erotundo/git/OSX-System-Logger/launchd_config/com.apple.energyprofiler.plist ~/Library/LaunchAgents/com.apple.energyprofiler.plist
	```
1. Reboot your Mac
	
1. Check if scripts are working:
	
	```
	tail -f /Users/erotundo/git/energyprofiler/Code/macLogger/log.txt
	```
	
	
### Uninstall

TODO