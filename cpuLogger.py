#!/usr/bin/python

import subprocess
import shlex
import time
import getpass


logFilename = "logs/" + getpass.getuser() + "_cpu.csv"

def myrun(cmd):    
    out_file = open(logFilename,"a", 0)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline().replace('\n','')
        stdout.append(line)
        
        if line.replace(' ','').isdigit():
            record = time.strftime("%a %b %d %X %Z %Y") + "," + line.split()[0] + ","+ line.split()[1] + "," + line.split()[2]
            # print record
            out_file.write(record + "\n")

        if line == '' and p.poll() != None:
            break

    return ''.join(stdout)
try:
    myrun("iostat -w 1 -n 0 -Cd")
except Exception, e:
    "Unexpected error:", sys.exc_info()[0]
finally:
    print "closing... " + file
    out_file.close()