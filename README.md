# OSX System Logger

### Requirements:

* Command line tools installed (*gcc*, xcode)
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

1. Run ```echo "PASSWORD" >> remote.txt```, ask Enrico which is the password

1. Run **(IMPORTANT: before running this, unplug every usb devices connected!)**:

	```
	ioreg -p IOUSB -w0 | sed 's/[^o]*o //; s/@.*$//' | grep -i -v '^Root.*' > usbDevices_config.txt
	```

1. Change folder

	```
	cd launchd_config/
	```
	
1. Create launchd plist files from template (they must not be writable by anyone other than the owner!)
	
	```
	cp com.apple.energyprofiler.lastDump.plist.template com.apple.energyprofiler.lastDump.plist
	cp com.apple.energyprofiler.ntpUpdater.plist.template com.apple.energyprofiler.ntpUpdater.plist
	cp com.apple.energyprofiler.sysLogger.plist.template com.apple.energyprofiler.sysLogger.plist
	```

1. Change ```ntpUpdater.plist``` owner: 

	```
	sudo chown root com.apple.energyprofiler.ntpUpdater.plist
	```
		
1. In every ```.plist``` file there is the following XML elements couple:

	```
	<key>WorkingDirectory</key>
    <string>/Users/erotundo/git/OSX-System-Logger/</string>
    ```

	Replace the *string* XML element content with your repository absolute path 

1. Create user's launchd symlinks
	
	```
	ln -s "$PWD"/com.apple.energyprofiler.lastDump.plist ~/Library/LaunchAgents/com.apple.energyprofiler.lastDump.plist
	ln -s "$PWD"/com.apple.energyprofiler.sysLogger.plist ~/Library/LaunchAgents/com.apple.energyprofiler.sysLogger.plist
	```

1. Create root's launchd symlinks

	```
	sudo ln -s "$PWD"/com.apple.energyprofiler.ntpUpdater.plist /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist
	```
1. Install *psutil* (you may need *gcc*):
	
	1. 
		```
		cd
		
		git clone https://github.com/giampaolo/psutil.git
		
		cd psutil

		make install
		```
1. Install *paramiko*

	```
	sudo easy_install pip
	pip install paramiko
	```

1. **REBOOT THE SYSTEM** (not just Logout!)

1. Login *(this script assumes that you always use the same system user)*

1. DONE!

1. ... to check if scripts are actually working, run the following:
	
	```
	sudo launchctl list | grep energyprofiler
	```

	*should show something similar to:*

	```
	-	0	com.apple.energyprofiler.ntpUpdater
	```

	...and...

	```
	launchctl list | grep energyprofiler
	```

	*should show something similar to:*

	```
	2475	0	com.apple.energyprofiler.sysLogger
	-		0	com.apple.energyprofiler.lastDump
	```

	Furthermore, you can ```tail -f``` all the files in the ```logs/``` directory.
	

	NOTE: 

	1. If the second column reports not-zero means that and error occurred in the script execution
	1. First column is the PID of the running script (useful to monitor or kill the process)
	
	
### Uninstall

1. Remove launchd configurations

	```
	sudo mv -v /Library/LaunchDaemons/com.apple.energyprofiler.ntpUpdater.plist ~/.Trash/
	mv -v ~/Library/LaunchAgents/com.apple.energyprofiler.* ~/.Trash/
	```

1. Goto ```System Preferences``` pane, then select ```Date & Time``` and enable ```Set date and time automatically```, choose a preferred Apple NTP server from the dropdown list.

1. Reboot

### For questions ask to:
Enrico Rotundo - <enrico.rotundo@gmail.com>


# Linux:
```
sudo apt-get install python-pip
sudo apt-get install python-dev
sudo pip install psutil 
sudo apt-get install acpi
sudo apt-get install xbacklight
```
