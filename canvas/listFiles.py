#!/usr/local/bin/python3

import re
import os

def listFiles():
    print("==================================================", flush=True)
    print("* List of submitted files are:", flush=True)
    files = os.listdir('.')
    # print("Found",len(files), "files and directories")
    pat = "^tester_.*$"
    prog = re.compile(pat)
    files = [f for f in files if os.path.isfile(f) and f[0] != '.' and (not prog.match(f))]
    print(files)
    print("==================================================", flush=True)


listFiles()    
