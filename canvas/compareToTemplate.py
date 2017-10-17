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
    if len(sys.argv) != 3:
        sys.exit(format("usage: %s file1 file2 -- needs 2 parameters, got: %s" %
                        (os.path.basename(__file__), " ".join(sys.argv))))
    jollyhelper.compareToTemplate(sys.argv[1], sys.argv[2])
