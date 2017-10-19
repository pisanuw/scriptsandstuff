#!/usr/bin/env python
"""
Call the function from jollyhelper directly through a script
This is useful, so we can use the subprocess mechanism and easily
timeout or kill the script
"""

import sys
import jollyhelper


if __name__ == "__main__":
    jollyhelper.cCompileRun(sys.argv[1:])
