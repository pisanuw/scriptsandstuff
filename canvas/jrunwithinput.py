#!/usr/local/bin/python3

import subprocess
import os
import sys
import re
import tempfile

# run the given file with the inputs given
#
# Compile all files in directory and run them with the input foo.txt
# jrunwithinputs foo.txt
#
# Compile Coffee.java and run it with the input foo.txt
# jrunwithinputs Coffee foo.txt

def jcompile(j):
    jf = j + ".java"
    jc = j + ".class"
    if not os.path.isfile(jf):
        print("XXX Could not find %s to compile" % jf)
        return
    #Only compile if necessary
    #if (os.path.isfile(jc)):
    #    os.remove(jc)
    if not os.path.isfile(jc):
        result = subprocess.run(["javac", jf])
    if os.path.isfile(jc):
        print("Compiled %s successfully" % jf, flush=True)
        return True;
    else:
        print("XXX Failed to compile %s" % jf, flush=True)
        return False;

def getJavaFiles():
    jfiles = []
    files = os.listdir('.')
    pat = "^(.*).java$"
    prog = re.compile(pat)
    for f in files:
        if os.path.isfile(f):
            result = prog.match(f)
            if result:
                jfiles.append(result.group(1))
    return jfiles;
    
def jRunWithInput(prog, infile):
    print("\n==================================================", flush=True)
    print("* Running java %s < %s" % (prog, infile), flush=True)
    print("==================================================", flush=True)
    with subprocess.Popen(["java", "-ea", prog], stdin=subprocess.PIPE) as proc:
        with open(infile) as f:
            lines = f.readlines()
            print("Input lines are:\n%s" % lines, flush=True)
            proc.stdin.write(bytes("".join(lines), 'utf-8'))

def jcompileAndRun(infile):
    print("\n==================================================", flush=True)
    jfiles = getJavaFiles();
    for j in jfiles:
        if jcompile(j):
            jRunWithInput(j, infile)
    print("\n==================================================", flush=True)            





if len(sys.argv) < 2:
    print("Need at least 1 argument to jrunwithinput")
elif len(sys.argv) == 2:
    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        print("*** Could not find inputfile %s for %s" % (inputFile, " ".join(sys.argv)))
        exit(-1)
    jcompileAndRun(inputFile)
elif len(sys.argv) == 3:
    javaFileGiven = sys.argv[1]
    inputFile = sys.argv[2]
    if not os.path.isfile(inputFile):
        print("*** Could not find inputfile %s for %s" % (inputFile, " ".join(sys.argv)))
        exit(-1)
    jRunWithInput(javaFileGiven, inp)
else:
    print("Too many arguments to jrunwithinput %s" % " ".join(sys.argv))


exit(0)
