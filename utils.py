import subprocess
import shlex
import os
devnull = open(os.devnull, 'wb')
# executes a bash command and returns the string output
def executeBashCmd(bashCommand):
	args = shlex.split(bashCommand)
	process = subprocess.Popen(args, stdout=subprocess.PIPE)
	output = process.communicate()[0]
	return output

def executeBashCmdNoErr(bashCommand):
	args = shlex.split(bashCommand)
	process = subprocess.Popen(args,  stdout=subprocess.PIPE, stderr=devnull)
	output = process.communicate()[0]
	return output

def cmdPiped(grepCmd):
	cmd1="ioreg -p IOUSB -w0" 
	cmd2="sed 's/[^o]*o //; s/@.*$//'"
	p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
	p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE)
	p3 = subprocess.Popen(shlex.split(grepCmd), stdin=p2.stdout, stdout=subprocess.PIPE)
	output = p3.communicate()[0]
	return output