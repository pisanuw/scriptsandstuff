# jollyFeedback


This project is under development. It is far from ready to be seen by other people or let alone run on other computers.

However, if you are an adventerous hacker, dive in and start playing around with things

## How to get started

- Download assignments from canvas

- unzip the file, lets call it ~/Downloads/submissions/

- On the command line, cd to ~/Downloads/submissions/ and execute jollyFeedback.py

- If all went well, you should now have lots of subdirectories under ~/Downloads/submissions/ where each subdirectory corresponds to a single student's file submissions

## Explore

try ``jollyFeedback.py --help`` to see the command-line options

```
usage: jollyFeedback.py [-h] [--dir DIR] [--testdir TESTDIR]
                        [--classlist CLASSLIST] [--helpdir HELPDIR]

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             submission directory where downloaded canvas files are
                        located, default . for current dir
  --testdir TESTDIR     tester scripts directory, test scripts must be named
                        test_xxx (no default, must be provided)
  --classlist CLASSLIST
                        csvfile for the classlist with student ids
  --helpdir HELPDIR     helper scripts directory, defaults to the directory
                        where this file is
```


try ``jollyhelper.py --help`` to see the command-line options

```
############################################
# Helper functions for Jolly
############################################
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
#
# mailSendFile(fromemail, toEmail, subject, textfile, fromname="",
#                authfile='~/private/jollyauth.txt',
#                smtpserver='smtp.uw.edu',
#                filetosaveemail="tester_emailedfile.txt", timedelay=15, reallysend=False):

```

Have a look at ```test_sample.py``` to see how a testing script can be written. jollyFeedback will execute wll athe testing scripts matching the pattern test_ in the directory supplied by --testdir TESTDIR


Happy to receive feedback!


Yusuf Pisan
pisan[at]uw.edu
