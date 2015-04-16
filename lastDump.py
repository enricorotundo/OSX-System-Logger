#!/usr/bin/python

import getpass
import time
from scp import SCPClient
import paramiko
import tarfile
import os
import sys
from utils import executeBashCmd

loginCmd = "last" # get login history
lastLog = "logs/" + getpass.getuser() + "_last.txt"

def lastFileDump():
	last_file = open(lastLog,"a", 0)
	last_file.write(executeBashCmd("last"))
	last_file.close()
	return

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def main():
    
    # print "opening ssh tunnel"
    conf = open("remote.txt","r").readline().replace("\n","")
    ssh = createSSHClient("vps142403.ovh.net", 22, "energy", conf)
    scp = SCPClient(ssh.get_transport())
    # print "ssh tunnel opened"
    
    outFile = getpass.getuser() + "_" + time.strftime("%m%d%Y_%H%M") + "_logs.tar.gz"
    
    lastFileDump()

    make_tarfile(outFile, "logs")
    # print "created: " + outFile 

    # print "coping file"
    scp.put(outFile, outFile)
    #  print "copy finished"

    print >> sys.stderr, time.strftime("%m%d%Y_%H%M") + ' Error occurred'
    # time.sleep(120) # wait 2 minutes before

    try:
        os.remove(outFile)
    except OSError:
        pass

    time.sleep(12)


if __name__ == '__main__':
    main()