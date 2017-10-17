#!/usr/bin/env python
"""
Call the function from jollyhelper directly through a script
This is useful, so we can use the subprocess mechanism and easily
timeout or kill the script
"""

import os
import sys
import jollyhelper


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(format("usage: %s templatefile [file1 file2 ...]  -- needs at least 1 parameters, got: %s" %
                        (os.path.basename(__file__), " ".join(sys.argv))))
    jollyhelper.cRunCompareOutput(sys.argv[1], sys.argv[2:])
