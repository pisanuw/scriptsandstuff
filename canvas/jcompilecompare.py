#!/usr/local/bin/python3

import tempfile
import subprocess
import os
import sys
import re
import argparse

# when no filename given try to compile and run all java files

parser = argparse.ArgumentParser()
parser.add_argument("--compileonly", help="only compile, no run", action='store_true')
parser.add_argument("--template", help="template file to compare to", required=True)
args = parser.parse_args()

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
    if not args.compileonly:
        print("\n* Running " + f + "\n", flush=True)
        result = subprocess.run(["java", "-ea", f])
        if result.returncode:
            print("XXX Running error", flush=True)        
        else:
            print("    ran successfully\n", flush=True)       
            ftmp = tempfile.NamedTemporaryFile(delete=False)
            # print("Created a temporary file called: %s" % f.name)
            # f.write(b"Hello World")
            ftmp.close()
            with open(ftmp.name, "w") as outfile:
                result = subprocess.call(["java", "-ea", f], stdout=outfile, stderr=outfile)
            print("\n========================================\n", flush=True)
            print("Comparing output produced to template file")
            print("\n========================================\n", flush=True)
            result = subprocess.run(["diff", "-C1", "--suppress-common-lines", ftmp.name, args.template])                
            print("\nEnd of comparison. If the above part is empty,")
            print("your output is identical to the template. Congratulations!")
            print("\n========================================\n", flush=True)
            os.unlink(ftmp.name)


filesToCompile = sys.argv[3:]

args.template = os.path.abspath(os.path.expanduser(args.template))

if not os.path.isfile(args.template):
    print("jcompilecompare.py could not find template file %s" % args.template)
    exit(-1)

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
