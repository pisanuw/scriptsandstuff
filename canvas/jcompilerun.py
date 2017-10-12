#!/usr/local/bin/python3

import subprocess
import os
import sys
import re
import argparse

# when no filename given try to compile and run all java files

parser = argparse.ArgumentParser()
args = parser.parse_args()
parser.add_argument("--compileonly", help="only compile, no run")

if (args.compileonly):
    print("Yes comp only")
else:
    print("No comp only")
    
def jtestCompileRun(f):
    jf = f + ".java"
    jc = f + ".class"
    print("==================================================", flush=True)
    print("* Compiling %s" % f, flush=True)
    print("==================================================", flush=True)
    if not os.path.isfile(jf):
        print("XXX Could not find %s to compile" % jf)
        return
    if (os.path.isfile(jc)):
        os.remove(jc)
    result = subprocess.run(["javac", jf])
    if os.path.isfile(jc):
        print("Compiled %s successfully" % jf, flush=True)
    else:
        print("XXX Failed to compile %s" % jf, flush=True)
        return;
    if (args.compileonly):
        print("\n* Running " + f + "\n", flush=True)
        result = subprocess.run(["java", "-ea", f])
        if result.returncode:
            print("XXX Running error", flush=True)        
        else:
            print("    ran successfully\n", flush=True)       


filesToCompile = sys.argv[1:]

if (len(filesToCompile) == 0):
    files = os.listdir('.')
    pat = "^(.*).java$"
    prog = re.compile(pat)
    for f in files:
        if os.path.isfile(f):
            result = prog.match(f)
            if result:
                filesToCompile.append(result.group(1))
    print(filesToCompile)

for f in filesToCompile:
    jtestCompileRun(f)


exit(0)
