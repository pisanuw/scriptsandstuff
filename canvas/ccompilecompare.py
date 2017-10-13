#!/usr/local/bin/python3

import subprocess
import os
import sys
import re
import argparse
import tempfile

# compile the files and compare them to the expected output given


parser = argparse.ArgumentParser()
parser.add_argument("--compileonly", help="only compile, no run", action='store_true')
parser.add_argument("--template", help="template file to compare to", required=True)
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
            f = tempfile.NamedTemporaryFile(delete=False)
            # print("Created a temporary file called: %s" % f.name)
            # f.write(b"Hello World")
            f.close()
            with open(f.name, "w") as outfile:
                result = subprocess.call([dst], stdout=outfile, stderr=outfile)
            print("\n========================================\n", flush=True)
            print("Comparing output produced to template file")
            print("\n========================================\n", flush=True)
            result = subprocess.run(["diff", "-C1", "--suppress-common-lines", f.name, args.template])                
            print("\nEnd of comparison. If the above part is empty,")
            print("your output is identical to the template. Congratulations!")
            print("\n========================================\n", flush=True)
            os.unlink(f.name)


filesToCompile = sys.argv[3:]

args.template = os.path.abspath(os.path.expanduser(args.template))

if not os.path.isfile(args.template):
    print("ccompilecompare.py could not find template file %s" % args.template)
    exit(-1)
    
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
