#!/usr/local/bin/python3
"""Test assignment submissions"""

import sys
import os
import argparse

########################################################################################
# You should not modify this section
# All tests go below to [TESTING AREA]
########################################################################################

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--helpdir", default="~/bitbucket/scriptsandstuff/canvas",
                    help="helper scripts directory, \
                    defaults to the directory for jollyhelper.py is (default: %(default)s)'")

HELPDIR = os.path.abspath(os.path.expanduser(PARSER.parse_args().helpdir))

if not os.path.isdir(HELPDIR):
    print("*** %s called with a bad HELPDIR directory >%s<: %s" %
          (__file__, HELPDIR, " ".join(sys.argv)))
    sys.exit(-1)

MYDIR = os.path.dirname(os.path.realpath(__file__))

# This file is one of the test files called from jollyFeedback.py
# The helper scripts and helper python files are in the jollyFeedback directory

sys.path.insert(0, HELPDIR)
import jollyhelper

########################################################################################
# Helper functions from jollyhelper also available as standalone scripts
# jollyhelper.listFiles()  OR
# runHelper("listFiles.py")
#
# Running functions directly is faster, less overhead
# Running via runHelper is necessary for timeouts when programs hang
########################################################################################
# Functions available
########################################################################################
# listFiles() -- list files in directory except files created by Jolly which are tester_xxx
# compareFiles(file1, file2) -- compare files using diff
# compareToTemplate(studentfile, templateFile): -- compare files, template is in script directory
# renameIfPossible(src, dest) -- rename files
# javaCompile(givenfile=None):  compile a java file, if no filename, compile all
# javaRun(givenfile=None): - run a java file, if no filename run all class files
# javaCompileRun(givenfile=None): - compile and run a java file, if no filename compile and run all
# javaRunCompareOutput(file, templateFile) - compile, run and compare output to template
# javaCleanClassFiles()
# C versions
# cCompile, cRun, cCompileRun, cRunCompareOutput, cCleanExeFiles
##################################################
# Scripts Available
##################################################
# cCleanExeFiles.py
# cCompile.py
# cCompileRun.py
# cRun.py
# cRunCompareOutput.py
# cRunWithInput.py
# cStyleChecker.py
# compareFiles.py
# compareToTemplate.py
# javaCleanClassFiles.py
# javaCompile.py
# javaCompileRun.py
# javaRun.py
# javaRunCompareOutput.py
# javaRunWithInput.py
# jollyFeedback.py
# jollyhelper.py
# listfiles.py
# mailSendFile.py
# renameIfPossible.py
# testPythonVersion.py
#
# usage: mailSendFile.py [-h] --fromemail FROMEMAIL [--toemail TOEMAIL]
#                       [--subject SUBJECT] [--filetosend FILETOSEND]
#                       [--fromname FROMNAME] [--smtpauthfile SMTPAUTHFILE]
#                       [--smtpserver SMTPSERVER]
#                       [--filetosaveemail FILETOSAVEEMAIL]
#                       [--timedelay TIMEDELAY] [--reallysend]
#                       [--fileforintrotext FILEFORINTROTEXT]
#mailSendFile.py: error: the following arguments are required: --fromemail
#
#jollyhelper.runHelper(mailSendFile(fromEmail=None,
#                 toEmail=None,
#                 subject='Comments from JollyFeedback Automated Script',
#                 filetosend='tester_logfile.txt',
#                 fromname=None,
#                 fileforintrotext=None,
#                 authfile='~/private/jollyauth.txt',
#                 smtpserver='smtp.uw.edu',
#                 filetosaveemail="tester_emailedfile.txt",
#                 timedelay=15, reallysend=False):
# The only requirement for mailSendFile is 'fromEmail'
#
########################################################################################
#
# [TESTING AREA]
#
########################################################################################

jollyhelper.cCleanExeFiles()
jollyhelper.runHelper("listFiles.py")
jollyhelper.cCompile()
jollyhelper.cRunWithInputOutput(os.path.join(MYDIR, "input-0.txt"), os.path.join(MYDIR, "output-0.txt"), "coffeeorder.c")
jollyhelper.cRunWithInput(os.path.join(MYDIR, "input-5.txt"), "coffeeorder.c")
jollyhelper.cRunWithInputOutput(os.path.join(MYDIR, "input-132.txt"), os.path.join(MYDIR, "output-132.txt"), "coffeeorder.c")

jollyhelper.runHelper("mailSendFile.py",
                      [
                          "--fromemail", "pisan@uw.edu", "--fromname", "Yusuf Pisan",
                          "--subject", "CSS 132: Comments from JollyFeedback on coffeeorder.c",
                          "--fileforintrotext", os.path.join(MYDIR, "emailintro.txt"),
                        # BE CAREFULL -- DO NOT SPAM PEOPLE
                        #  "--reallysend"
                          ],
                      timeout=200)
