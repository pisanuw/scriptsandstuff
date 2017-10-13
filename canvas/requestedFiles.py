#!/usr/local/bin/python3

import re
import os
import sys

def requestedFiles(fileList):
    seen = {}
    print("==================================================", flush=True)
    print("* List of submitted files are:", flush=True)
    files = os.listdir('.')
    # print("Found",len(files), "files and directories")
    pat = "^tester_.*$"
    prog = re.compile(pat)
    files = [f for f in files if os.path.isfile(f) and f[0] != '.' and (not prog.match(f))]
    for f in files:
        seen[f] = True
    print(files)
    for f in fileList:
        if f not in seen:
            print("ALERT: Missing file: %s" % f)
    print("==================================================", flush=True)


requestedFiles(sys.argv[1:])    

