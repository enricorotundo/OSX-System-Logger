#!/usr/bin/python

import getpass
import time
from scp import SCPClient
import paramiko
import tarfile
import os
import sys
import glob
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

    # THIS SCRPIT WILL BE RELAUNCED UNTIL IT EXITS WITH STATUS CODE: 0
    time.sleep(5)

    # COMPRESS ALL CSV FILES EXCEPT THE ONE OF TODAY
    pastCSVfiles = glob.glob("logs/" + getpass.getuser() + "_log_" + "*.csv")
    for csvFile in pastCSVfiles:
        if csvFile != ("logs/"+getpass.getuser()+"_log_"+time.strftime("%m%d%Y")+".csv"):
            outFile = csvFile[:-3] + "tar.gz"
            try:
                make_tarfile(outFile, csvFile)                
                try:
                    os.remove(csvFile)
                except OSError:
                    print "error removing: " + csvFile
            except:
                print "error creating or compressing: " + outFile

    # COMPRESS TXT AND LOG FILES
    otherFiles = glob.glob("logs/*.txt") + glob.glob("logs/*.log")
    for file in otherFiles:
        outFile =  file[:5] + getpass.getuser() + "_" + file[5:-3]  + "tar.gz"
        try:
            make_tarfile(outFile, file)
        except:
            print "error creating or compressing: " + outFile
    
    
    # OPEN SSH CONNECTION
    conf = open("remote.txt","r").readline().replace("\n","")
    ssh = createSSHClient("vps142403.ovh.net", 22, "energy", conf)
    scp = SCPClient(ssh.get_transport())

    # UPLOAD TAR GZ FILES
    compressedFiles = glob.glob("logs/*.tar.gz")
    for file in compressedFiles:
        scp.put(file)
        os.rename(file, file + ".uploaded")


    time.sleep(5)


if __name__ == '__main__':
    main()