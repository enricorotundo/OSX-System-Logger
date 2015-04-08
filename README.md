# OSX-System-Logger





### Requirements:

* command line tools installed (Xcode)
* python 2.7 installed 
* sudo

```
ioreg -p IOUSB -w0 | sed 's/[^o]*o //; s/@.*$//' | grep -i -v '^Root.*' > usbDevices_config.txt
```

### Install (Mac OSX 10.10.2):

1. Clone the repo:

	```
	git clone https://github.com/tundo91/OSX-System-Logger.git
	```

1. set the NTP server (important):

	```
# 	sudo ntpdate -u ntp1.inrim.it
	```
	
1. goto macLogger directory
	
	```
	cd Code/macLogger/
	```
	
1. create new launchd plist from template (it must not be writable by anyone other than the owner)
	
	```
	cp com.apple.energyprofiler.plist.template com.apple.energyprofiler.plist
	```
		
1. modify the plist file by replacing paths with your local "macLogger" absolute path. The "pwd" command gets the abs path of the current dir.

1. create launchd symlink
	
	```
	ln -s /Users/erotundo/git/energyprofiler/Code/macLogger/com.apple.energyprofiler.plist ~/Library/LaunchAgents/com.apple.energyprofiler.plist
	```
1. to check if the script is working:
	
	```
	tail -f /Users/erotundo/git/energyprofiler/Code/macLogger/log.txt
	```
	
	
### Uninstall

1. Revert original Apple NTP server. 

	```
	sudo ntpdate -u ntp1.inrim.it
	```
