#!/usr/local/bin/python3

import subprocess
import os
import sys

# The first file is submitted by student and is in current directory
# The second file is template and is in same directory as testing script        
def compareFiles(studentfile, template):
    testerPath = os.path.dirname(os.path.realpath(__file__))
    template = os.path.join(testerPath, template)
    print("==================================================", flush=True)
    print("* Comparing %s to the template file" % studentfile, flush=True)
    print("==================================================", flush=True)
    print("Comparison is to make it easier to pinpoint differences.", flush=True)
    print("These are not errors, just places to pay attention to.", flush=True)
    if not os.path.isfile(studentfile):
        print("XXX Could not find %s to compare" % studentfile)
        return
    if not os.path.isfile(template):
        print("XXX Could not find template file %s to compare" % template)
        return    
    result = subprocess.run(["diff", "-C1", "--suppress-common-lines", studentfile, template])
    print(testerPath)


if (len(sys.argv) == 3):    
    student = sys.argv[1]
    temp = sys.argv[2]
    compareFiles(student, temp)
    exit(0)
else:
    print("Bad call to compareFiles: %s" % " ".join(sys.argv), file=sys.stderr)
    exit(-1)        


