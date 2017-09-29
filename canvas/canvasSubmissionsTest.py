#!/usr/local/bin/python3

# Move all files in current directory to subdirectories based on student name or student number

import sys
import csv
import os
import subprocess
import datetime
import argparse


dirSep = os.sep

class Student():
    def __init__(self, number='', netid='', fname='', lname='', email=''):
        self.number = number
        self.netid = netid
        self.fname = fname
        self.lname = lname
        self.email = email

        
# Student Number	UW NetID	Name	Last Name	Credits	Class	Majors	Email
# 
studentInfo = { }

# The UW student list is in the form of
# Student Number	UW NetID	Name	Last Name	Credits	Class	Majors	Email
def readStudentList(classList):
    with open(classList) as csvfile:
        classReader = csv.reader(csvfile, delimiter=',')
        for row in classReader:
            studentInfo[row[0]] = Student(row[0],row[1],row[2],row[3],row[7])

def bfile2ok(filename):
    return 4 == len(filename.split('_'))

# canvas files are lastnamefirstname_studentnumber_someothernumber_actualsubmittedfile
def bfile2submitted(filename):
    (lastfirst, num, mysterynum, actualsubmitted) = filename.split('_')
    return actualsubmitted

def bfile2studentnumber(filename):
    (lastfirst, num, mysterynum, actualsubmitted) = filename.split('_')
    return num


def moveFiles():
    global dirSep
    base = '.'
    files = os.listdir()
    print("Found",len(files), "files and directories")    
    files = [f for f in files if os.path.isfile(f)]
    print("Found",len(files), "files: ", files)
    count = 1
    for file in files:
        print(count," processing", file)
        if bfile2ok(file):
            studentnum = bfile2studentnumber(file)
            newdir = studentnum
            sfileRel = studentnum + dirSep + bfile2submitted(file)
            if (not os.path.exists(newdir)):
                print("   Making ", newdir)
                os.mkdir(newdir)
            print("   Renaming ", file, " to ", sfileRel)
            os.rename(file, sfileRel)
        else:
            print("*** Skipping bad file: ", file)
        count = count + 1
    

def runtests(tdir, submitdir):
    global dirSep
    testerlog = "tester_logfile.txt"
    print("Test directory is %s" % tdir)
    tfiles = os.listdir(tdir)
    tfiles = [f for f in tfiles if os.path.isfile(tdir + dirSep + f) and f.startswith("test_") ]
    print("Found",len(tfiles), "files: ", tfiles)
    sdirs = os.listdir()
    sdirs = [f for f in sdirs if os.path.isdir(f)]
    print("Found",len(sdirs), " student directories: ", sdirs)
    for d in sdirs:
        os.chdir(submitdir)
        os.chdir(d)
        logfile = submitdir + dirSep + d + dirSep + testerlog
        if os.path.isfile(logfile):
            print("Removing old logfile %s" % logfile)
            os.remove(logfile)
        print("Looking at %s" % d)
        with open(logfile, "a") as outfile:
            for tt in tfiles:
                print("---> Calling %s" % tt)
                outfile.write("Starting tests at: %s\n\n"  % datetime.datetime.now())
                outfile.flush()
                result = subprocess.call([tdir + dirSep + tt, "   "], stdout=outfile, stderr=outfile)
                if (result):
                    print("<--- Failed %s " % tt)
                else:
                    print("<--- Completed %s successfully" % tt)
                outfile.write("\n\nFinished tests at: %s\n\n\n"  % datetime.datetime.now())
        
    
    
def main():
    global dirSep
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_directory", help="directory for submissions, use . for current dir")
    parser.add_argument("--classlist", help="csvfile for the classlist including student numbers")
    parser.add_argument("--testdir", help="directory for test scripts to be executed, test scripts must be named test_xxx")
    args = parser.parse_args()
    print("Current time: %s"  % datetime.datetime.now())
    print("Changing directory to ", args.submission_directory)
    os.chdir(args.submission_directory)
    args.submission_directory = args.submission_directory.rstrip(dirSep)
    moveFiles()
    if (args.testdir):
        if (os.path.isdir(args.testdir)):
            args.testdir = args.testdir.rstrip(dirSep)
            runtests(args.testdir, args.submission_directory)
        else:
            print("*** Test directory %s is not valid" % args.testdir)


main()


