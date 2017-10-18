#!/usr/local/bin/python3


# Move all files in current directory to subdirectories based on student name or student number

import sys
import csv
import os
import subprocess
import time
import argparse
import re

TIMEOUT = 20

class Student():
    def __init__(self, lastfirst='', number='', netid=''):
        self.lastfirst = lastfirst
        self.number = number
        self.netid = netid
    def __str__(self):
        return "<S: " + " ".join([self.lastfirst, self.number, self.netid]) + ">"





studentInfo = [ ]

# The UW student list is in the form of
# Student Number	UW NetID	Name	Last Name	Credits	Class	Majors	Email
# def readStudentListmyUWCSV(classList):a
#     with open(classList) as csvfile:
#         classReader = csv.reader(csvfile, delimiter=',')
#         for row in classReader:
#             studentInfo[row[0]] = Student(row[0],row[1],row[2],row[3],row[7])


# Canvas download grades gives you a csv file of the form
# Student, ID, SIS User ID, SIS Login ID, Section
# Student is Lastname, Firstname Middlename
def readStudentListCanvasCSV(classList):
    with open(classList) as csvfile:
        classReader = csv.reader(csvfile, delimiter=',')
        # skip 2 header lines
        next(classReader)
        next(classReader)
        for row in classReader:
            studentInfo.append(Student(row[0],row[1],row[3]))

def printStudentList():
    for s in studentInfo:
        print(s)

# canvas files are lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile-version.extension
def bfile2ok(filename):
    ln = len(filename.split('_'))
    # file can have 5 parts when late, 6 or more if _ part of file name
    return (ln >= 4)

def bfile2lateToNormal(filename):
    patlate = "^(.*)_late_(.*)$"
    prog = re.compile(patlate)
    result = prog.match(filename)
    if (result):
        filename = result.group(1) + "_" + result.group(2)
    return filename

# canvas files are lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile-version.extension
def bfile2submitted(filename):
    filename = bfile2lateToNormal(filename)
    parts = filename.split('_')
    assert(len(parts) >= 4)
    (lastfirst, num, mysterynum, actualsubmitted) = parts[:4]
    patversion = "^(.*)-[0-9]+.(.*)$"
    prog = re.compile(patversion)
    result = prog.match(actualsubmitted)
    if (result):
        actualsubmitted = result.group(1) + "." + result.group(2)
    return actualsubmitted
        
def bfile2studentnumber(filename):
    filename = bfile2lateToNormal(filename)
    parts = filename.split('_')
    assert(len(parts) >= 4)
    (lastfirst, num, mysterynum, actualsubmitted) = parts[:4]    
    return num

def bfile2studentdir(filename):
    filename = bfile2lateToNormal(filename)
    parts = filename.split('_')
    assert(len(parts) >= 4)
    (lastfirst, num, mysterynum, actualsubmitted) = parts[:4]
    # lets use just lastfirst, no student number
    # return lastfirst + "_" + num
    return lastfirst

def getStudentNetID(number):
    print("Looking for %s" % number)
    for s in studentInfo:
        if (number == s.number):
            return s.netid
    return 0

def moveFiles(submit):
    files = os.listdir(submit)
    print("Found",len(files), "files and directories")    
    files = [f for f in files if os.path.isfile(os.path.join(submit, f)) and f[0] != '.']
    print("Found",len(files), "files: ", files)
    count = 1
    for file in files:
        print(count," processing", file)
        if bfile2ok(file):
            filefull = os.path.join(submit, file)
            sdirfull = os.path.join(submit, bfile2studentdir(file))
            newfilefull = os.path.join(sdirfull, bfile2submitted(file))
            if (not os.path.exists(sdirfull)):
                print("   Making ", sdirfull)
                os.mkdir(sdirfull)
            print("   Renaming ", filefull, " to ", newfilefull)
            os.rename(filefull, newfilefull)
            # Add student UWNetID if possible
            snumber = bfile2studentnumber(file)
            sID = getStudentNetID(snumber)
            if (sID):
                sidFile = os.path.join(sdirfull, format("tester_netid_%s.txt" % sID))
                with open(sidFile, "w") as outfile:
                    outfile.write(sID)
        else:
            print("*** Skipping bad file: ", file)
        count = count + 1
    

def runtests(helpdir, testdir, submitdir):
    testerlog = "tester_logfile.txt"
    print("Test directory is %s" % testdir)
    testfiles = os.listdir(testdir)
    testfiles = [f for f in testfiles if os.path.isfile(os.path.join(testdir, f)) and f.startswith("test_") ]
    print("Found",len(testfiles), "files: ", testfiles)
    sdirs = os.listdir(submitdir)
    sdirs = [f for f in sdirs if os.path.isdir(os.path.join(submitdir, f))]
    print("Found",len(sdirs), " student directories: ", sdirs)
    for d in sdirs:
        dfull = os.path.join(submitdir, d)
        os.chdir(dfull)
        logfile = os.path.join(dfull, testerlog)
        if os.path.isfile(logfile):
            # print("Removing old logfile %s" % logfile)
            os.remove(logfile)
        print("Looking at %s" % d)
        # start recording tests
        # with open(logfile, "a") as outfile:
        #    outfile.write("Starting tests at: %s\n\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))
        testStartTime = format("Started tests at: %s\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))            
        for tesfile in testfiles:
            # each test opens the file to append
            with open(logfile, "a") as outfile:
                print("---> Calling %s" % tesfile, end='.')
                testfilefull = os.path.join(testdir, tesfile)
                outfile.flush()
                result = None
                try:
                    # Default helpdir is fine
                    result = subprocess.run([testfilefull, "--helpdir", helpdir], stdout=outfile, stderr=outfile, timeout=TIMEOUT)
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
            outfile.write(testStartTime)
            outfile.write("Finished tests at: %s\n\n\n"  % time.strftime("%Y-%m-%d %H:%M:%S"))
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="submission directory where downloaded canvas files are located, default . for current dir")
    parser.add_argument("--testdir", default=None, help="tester scripts directory, test scripts must be named test_xxx (no default, must be provided)")
    parser.add_argument("--classlist", help="csvfile for the classlist with student ids")
    parser.add_argument("--helpdir", default=None, help="helper scripts directory, defaults to the directory where this file is")
    args = parser.parse_args()

    if not args.dir:
        args.dir = "."
    args.dir = os.path.abspath(os.path.expanduser(args.dir))        
    if not os.path.isdir(args.dir):
        print("*** submission_directory %s is not a valid directory" % args.dir)
        sys.exit(-1)

    if args.classlist:
        args.classlist = os.path.abspath(os.path.expanduser(args.classlist))
        if (os.path.isfile(args.classlist)):
            print("Reading csv file %s" % args.classlist)
            readStudentListCanvasCSV(args.classlist)
            # printStudentList()
        else:
            print("*** classlist %s is not a valid file" % args.classlist)
            sys.exit(-1)

    if args.testdir is None:
        print("Not testing anything, just moving files")
    else:
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
        
    print("Current time: %s"  % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Changing directory to ", args.dir)
    moveFiles(args.dir)
    if not args.testdir is None:
        runtests(args.helpdir, args.testdir, args.dir)

main()


