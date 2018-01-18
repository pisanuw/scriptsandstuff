#!/usr/bin/env python3
"""jollyFeedback is the driver for moving files downloaded from canvas into their own directories
and then running all the test programs"""

import sys
if not sys.version_info >= (3, 5):
    print("%s needs python 3.5 or later" % __file__)
    sys.exit(-1)

# pylint: disable=wrong-import-position
import os
import subprocess
import time
import argparse
import re
import jollyhelper

TIMEOUT = 20


# canvas files are
# lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile-version.extension
def canvasFileIsOK(filename):
    ln = len(filename.split('_'))
    # file can have 5 parts when late, 6 or more if _ part of file name
    return ln >= 4

def canvasFile2lateToNormal(filename):
    patlate = "^(.*)_late_(.*)$"
    prog = re.compile(patlate)
    result = prog.match(filename)
    if result:
        filename = result.group(1) + "_" + result.group(2)
    return filename

# canvas files are
# lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile-version.extension
def canvasFile2part(filename, partNum):
    filename = canvasFile2lateToNormal(filename)
    parts = filename.split('_')
    assert len(parts) >= 4 and partNum >= 0 and partNum <= 3
    fileWithParts = parts[:4]
    # 0 lastnamefirstname
    # 1 studentnumber
    # 2 someothernumber
    # 3 actualsubmittedfile
    return fileWithParts[partNum]
    
def canvasFile2submitted(filename):
    actualsubmitted = canvasFile2part(filename, 3)
    patversion = "^(.*)-[0-9]+.(.*)$"
    prog = re.compile(patversion)
    result = prog.match(actualsubmitted)
    if result:
        actualsubmitted = result.group(1) + "." + result.group(2)
    return actualsubmitted

def canvasFile2studentnumber(filename):
    return canvasFile2part(filename, 1)

def canvasFile2studentdir(filename):
    return canvasFile2part(filename, 0)

def getNonDotFiles(directory):
    files = os.listdir(directory)
    files = [f for f in files if os.path.isfile(os.path.join(directory, f)) and f[0] != '.']
    return files

def getCanvasFiles(directory):
    files = getNonDotFiles(directory)
    files = [f for f in files if os.path.isfile(os.path.join(directory, f)) and canvasFileIsOK(f)]
    return files

def getAllSubdirectories(directory):
    dirs = os.listdir(directory)
    dirs = [f for f in dirs if os.path.isdir(os.path.join(directory, f))]
    return dirs

def moveFiles(submit, files):
    print("Found", len(files), "files")
    count = 1
    for file in files:
        # print(count, " processing", file)
        canvasFileFull = os.path.join(submit, file)
        studentDir = os.path.join(submit, canvasFile2studentdir(file)) 
        studentFile = os.path.join(studentDir, canvasFile2submitted(file))
        if not os.path.exists(studentDir):
            os.mkdir(studentDir)
        os.rename(canvasFileFull, studentFile)
        print(count, " Moving %s to %s" %
              (file, 
               os.path.join(os.path.basename(submit), canvasFile2studentdir(file))))
        # if this was a zip file, unzip it in that directory
        extension = os.path.splitext(studentFile)[1]
        if (extension == ".zip"):
            print("zip file found: %s" % file)
            jollyhelper.unzipSubmittedZip(studentFile, studentDir)
        # Add student UWNetID if possible
        snumber = canvasFile2studentnumber(file)
        sID = jollyhelper.getStudentNetID(snumber)
        sName = jollyhelper.getStudentName(snumber)
        if not sID is None:
            sFile = os.path.join(studentDir, format("tester_netid_%s.txt" % sID))
            with open(sFile, "w") as outfile:
                outfile.write(sID)
        if not sName is None:
            sNameWithUnderScore = jollyhelper.substCommaAndSpace(sName)
            sFile = os.path.join(studentDir, format("tester_name_%s.txt" % sNameWithUnderScore))
            with open(sFile, "w") as outfile:
                outfile.write(sName)
        count = count + 1

def runtests(helpdir, testdir, submitdir, onlystudent=None):
    testerlog = "tester_logfile.txt"
    print("Test directory is %s" % testdir)
    testfiles = os.listdir(testdir)
    testfiles = [f for f in testfiles
                 if os.path.isfile(os.path.join(testdir, f)) and f.startswith("test_")]
    print("Found", len(testfiles), "files: ", testfiles)
    sdirs = []
    if onlystudent is None:
        sdirs = os.listdir(submitdir)
        sdirs = [f for f in sdirs if os.path.isdir(os.path.join(submitdir, f))]
        print("Found", len(sdirs), " student directories: ", sdirs)
    else:
        dfull = os.path.join(submitdir, onlystudent)
        if not os.path.isdir(dfull):
            print("ALERT: Cannot find student directory %s " % dfull)
            return;
        sdirs = [onlystudent]
    for directory in sdirs:
        dfull = os.path.join(submitdir, directory)
        os.chdir(dfull)
        logfile = os.path.join(dfull, testerlog)
        if os.path.isfile(logfile):
            # print("Removing old logfile %s" % logfile)
            os.remove(logfile)
        print("Looking at %s" % directory)
        # start recording tests
        # with open(logfile, "a") as outfile:
        #    outfile.write("Starting tests at: %s\n\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))
        testStartTime = format("Started tests at: %s\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))
        with open(logfile, "a") as outfile:
            outfile.write(testStartTime)
        for tesfile in testfiles:
            testfilefull = os.path.join(testdir, tesfile)
            if not os.access(testfilefull, os.X_OK):
                 print("ALERT: testfile is not executable %s " % testfilefull)
                 continue
            # each test opens the file to append
            with open(logfile, "a") as outfile:
                print("---> Calling %s" % tesfile, end='.')
                outfile.flush()
                result = None
                try:
                    # Default helpdir is fine
                    result = subprocess.run([testfilefull, "--helpdir", helpdir],
                                            stdout=outfile, stderr=outfile, timeout=TIMEOUT)
                except subprocess.TimeoutExpired as err:
                    print("ALERT: Ran out of time when running %s " % testfilefull)
                    print("ALERT: Possible cause waiting for keyboard input")
                    print("ALERT: Possible cause infinite loop")
                    print("TimeoutExpired error: {0}".format(err))
                if result is None:
                    print(" [Failed] %s" % result)
                else:
                    print(" [Success]")
        # Finished all tests, record time
        with open(logfile, "a") as outfile:
            outfile.write("Finished tests at: %s\n\n\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))

def main():
    parser = argparse.ArgumentParser()
    # pylint: disable=line-too-long
    parser.add_argument("--dir", 
                        default=".",
                        help="submission directory where downloaded canvas files are located " +
                        "(default: %(default)s)")
    parser.add_argument("--zipfile",
                        default=None,
                        help="the zip file downloaded from canvas with all assignments, (default: %(default)s) " +
                        "Cannot have both --dir and zipfile. If both provided, zipfile overrides --dir")
    parser.add_argument("--testdir", default=None, help="tester scripts directory, test scripts must be named test_xxx (no default, must be provided)")
    parser.add_argument("--classlist", help="csvfile for the classlist with student ids")
    parser.add_argument("--studentonly", help="only run the test for this student")    
    parser.add_argument("--helpdir", default=None, help="helper scripts directory, defaults to the directory where this file is")
    args = parser.parse_args()

    if not args.zipfile is None:
        if not args.dir == '.':
            print("*** Cannot use --dir %s and --zipfile %s, choose one or the other" % (args.dir, args.zipfile))
            return
    args.dir = os.path.abspath(os.path.expanduser(args.dir))
    if not os.path.isdir(args.dir):
        print("*** submission_directory %s is not a valid directory" % args.dir)
        sys.exit(-1)

    if args.classlist:
        args.classlist = os.path.abspath(os.path.expanduser(args.classlist))
        if os.path.isfile(args.classlist):
            print("Reading csv file %s" % args.classlist)
            jollyhelper.readStudentListCanvasCSV(args.classlist)
            # printStudentList()
        else:
            print("*** classlist %s is not a valid file" % args.classlist)
            sys.exit(-1)

    if not args.testdir is None:
        args.testdir = os.path.abspath(os.path.expanduser(args.testdir))
        if not os.path.isdir(args.testdir):
            print("*** testdir should be a director for test scripts, %s is not a valid directory" % args.testdir)
            sys.exit(-1)

    if args.helpdir is None:
        args.helpdir = os.path.dirname(os.path.realpath(__file__))
    args.helpdir = os.path.abspath(os.path.expanduser(args.helpdir))
    if not os.path.isdir(args.helpdir):
        print("*** helpdir should be a directory for helper scripts, %s is not a valid directory" % args.helpdir)
        sys.exit(-1)
    if not args.zipfile is None:
        args.zipfile = os.path.abspath(os.path.expanduser(args.zipfile))
        if os.path.isfile(args.zipfile):
            targetDir = jollyhelper.unzipSubmissions(args.zipfile)
            if targetDir is None:
                print("*** Failed to unzip %s" % args.zipfile)
                return
            if not os.path.isdir(targetDir):
                print("*** Unzipped %s, but could not find directory % for the files%s" % (args.zipfile, targetDir))
                return
            args.dir = targetDir
        else:
            print("*** zipfile %s could not be found" % args.zipfile)
            return
    canvasFiles = getCanvasFiles(args.dir)
    subdirectories = getAllSubdirectories(args.dir)
    if len(canvasFiles) == 0 and len(subdirectories) == 0:
        print("*** No canvas files of the form\n" +
              "lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile-version.extension\n" +
              "was found in %s." % args.dir)
        print("Try calling %s with --zipfile or --dir" % os.path.basename(__file__))
        return
    # print("Current time: %s"  % time.strftime("%Y-%m-%d %H:%M:%S"))
    # print("Changing directory to ", args.dir)
    files = getCanvasFiles(args.dir)
    if len(files) > 0:
        moveFiles(args.dir, files)
    if args.testdir is None:
        print("*** Not doing any testing, use --testdir to specify tests")
    else:
        runtests(args.helpdir, args.testdir, args.dir, args.studentonly)

# let's make this happen
main()
