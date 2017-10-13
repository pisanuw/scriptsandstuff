#!/usr/local/bin/python3

import subprocess
import os
import sys
import re
import argparse

# when no filename given try to compile and run all java files

parser = argparse.ArgumentParser()
parser.add_argument("--compileonly", help="only compile, no run")
args = parser.parse_args()


def cCompileRun(f):
    src = f + ".c"
    dst = f + ".exe"
    print("==================================================", flush=True)
    print("* Compiling %s" % src, flush=True)
    print("==================================================", flush=True)
    if not os.path.isfile(src):
        print("XXX Could not find %s to compile" % src)
        return
    if (os.path.isfile(dst)):
        os.remove(dst)
    result = subprocess.run(["gcc", "-Wall", "-o", dst ,   src])
    if os.path.isfile(dst):
        print("Compiled %s successfully" % dst, flush=True)
    else:
        print("XXX Failed to compile %s" % src, flush=True)
        return;
    if not args.compileonly:
        print("\n* Running " + dst + "\n", flush=True)
        result = subprocess.run([dst])
        if result.returncode:
            print("XXX Running error", flush=True)        
        else:
            print("    ran successfully\n", flush=True)       


filesToCompile = sys.argv[1:]

if (len(filesToCompile) == 0):
    files = os.listdir('.')
    pat = "^(.*).c$"
    prog = re.compile(pat)
    for f in files:
        if os.path.isfile(f):
            result = prog.match(f)
            if result:
                filesToCompile.append(result.group(1))
    print(filesToCompile)

for f in filesToCompile:
    cCompileRun(f)


exit(0)
