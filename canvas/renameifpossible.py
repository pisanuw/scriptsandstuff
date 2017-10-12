#!/usr/local/bin/python3

import subprocess
import os
import sys
from shutil import copyfile

# Call this function with lots of variations
# First param is teh desired destination, the rest are possibilities for files submitted
# If the assignment was supposed to be name CoffeeOrder.c, we might use
# renameifpossible CoffeeOrder.c Coffeeorder.c coffeeorder.c Coffee_Order.c coffee_order.c coffee.c
# to get the correct file name
# This will not work with java since the filename is linked to class name



def renameIfPossibble(src, dest):
    if not os.path.isfile(src) or os.path.isfile(dest):
        return;
    print("==================================================", flush=True)
    print("* Copying %s to %s to help with other tests" % (src, dest), flush=True)
    print("==================================================", flush=True)
    copyfile(src, dest);
    if not os.path.isfile(dest):
        print("XXX Failed to copy %s to %s" % (src, dest))
    else:
        print("Successfully opied %s to %s" % (src, dest))        
    print("==================================================", flush=True)    


if len(sys.argv) > 2:
    dest = sys.argv[1]
    sources = sys.argv[2:]
    for s in sources:
        renameIfPossibble(s, dest)



exit(0)
