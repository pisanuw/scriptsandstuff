#!/usr/bin/env python
"""Helper files for JollyFeedBack"""

import sys
if not sys.version_info >= (3, 5):
    print("%s needs python 3.5 or later" % __file__)
    sys.exit(-1)

# pylint: disable=wrong-import-position
import socket
import subprocess
import re
import os
import shutil
import tempfile
import time
import smtplib
import email.mime.text

TIMEOUT = 5
MAILTIMEDELAY = 15
TESTERPATH = os.path.dirname(os.path.realpath(__file__))
JAVACOMPILER = "javac"
JAVAVM = "java"
JAVAFLAGS = ["-ea"]
CCOMPILER = "gcc"
CFLAGS = ["-Wall", "-g", "-o"]

HELPERINFO = """
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
"""

def startHelpSeparator(msg, out=sys.stdout):
    print("* Start :" + msg, file=out)
    print("==================================================", file=out, flush=True)

def endHelpSeparator(msg, out=sys.stdout):
    print("\n" + "* End: " + msg, file=out)
    print("==================================================", file=out, flush=True)

def listFiles():
    """List the files, except for tester_ files created by Jolly"""
    helperMsg = format("listing files in directory")
    startHelpSeparator(helperMsg)
    files = os.listdir('.')
    pat = "^tester_.*$"
    prog = re.compile(pat)
    files = [f for f in files if os.path.isfile(f) and f[0] != '.' and (not prog.match(f))]
    print(files)
    endHelpSeparator(helperMsg)

def dirList(pat):
    files = os.listdir('.')
    prog = re.compile(pat)
    files = [f for f in files if os.path.isfile(f) and prog.match(f)]
    return files

def dirListJava():
    return dirList(".*.java$")

def dirListC():
    return dirList(".*.c$")

def compareFiles(file1, file2, label1=None, label2=None):
    if label1 is None:
        label1 = os.path.basename(file1)
    if label2 is None:
        label2 = os.path.basename(file2)
    helperMsg = format("comparing %s to %s" % (label1, label2))
    startHelpSeparator(helperMsg)
    stillOK = True
    print("Comparison is to make it easier to pinpoint differences.")
    print("These are not necessarily errors, just places to pay attention to.")
    if not os.path.isfile(file1):
        print("ALERT: Could not find %s to compare" % file1)
        stillOK = False
    if not os.path.isfile(file2):
        print("SCRIPT ERROR: Could not find template file %s to compare" % file2)
        stillOK = False
    if stillOK:
        result = subprocess.run(["diff", "--label", label1, "--label", label2,
                                 "--report-identical-files", "--unified=1",
                                 "--suppress-common-lines", file1, file2])
        if result.returncode > 1:
            print("SCRIPT ERROR: diff returned %d" % result)
    endHelpSeparator(helperMsg)

def compareToTemplate(studentfile, templateFile):
    """template file is located in __file__ directory """
    compareFiles(studentfile, os.path.join(TESTERPATH, templateFile))

def renameIfPossible(src, dest):
    if not os.path.isfile(src) or os.path.isfile(dest):
        return
    helperMsg = format("renaming %s to %s" % (src, dest))
    startHelpSeparator(helperMsg)
    print("ALERT: Were you supposed to submit %s?" % dest)
    shutil.copyfile(src, dest)
    if not os.path.isfile(dest):
        print("SCRIPT ERROR: Failed to copy %s to %s" % (src, dest))
    endHelpSeparator(helperMsg)

def genericFileComponents(file, srcExt, exeExt):
    srcmatch = re.compile("^(.*)" + srcExt + "$").match(file)
    exematch = re.compile("^(.*)" + exeExt + "$").match(file)
    if srcmatch:
        baseFile = srcmatch.group(1)
        srcFile = baseFile + srcExt
        exeFile = baseFile + exeExt
    elif exematch:
        baseFile = exematch.group(1)
        srcFile = baseFile + srcExt
        exeFile = baseFile + exeExt
    else:
        # assuming bare file
        baseFile = file
        srcFile = baseFile + srcExt
        exeFile = baseFile + exeExt
    return (baseFile, srcFile, exeFile)

def javaFile2Components(file):
    return genericFileComponents(file, ".java", ".class")

def cFile2Components(file):
    return genericFileComponents(file, ".c", ".exe")

def genericCompile(compiler, cFlags, srcFile, exeFile):
    helperMsg = format("compiling %s" % srcFile)
    startHelpSeparator(helperMsg)
    if os.path.isfile(srcFile):
        if os.path.isfile(exeFile):
            os.remove(exeFile)
        command = [compiler] + cFlags + [srcFile]
        result = subprocess.run(command)
        if result.returncode != 0 or not os.path.isfile(exeFile):
            print("ALERT: Failed to compile %s using %s" %
                  (srcFile, " ".join(command)), flush=True)
        if result.returncode == 0 and os.path.isfile(exeFile):
            print("Compiled %s and got %s" %(srcFile, exeFile))
    else:
        print("ALERT: Could not find %s to compile" % srcFile)
    endHelpSeparator(helperMsg)

def javaCompile(givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListJava()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    for file in files:
        (_javaBase, javaFile, javaClass) = javaFile2Components(file)
        genericCompile(JAVACOMPILER, [], javaFile, javaClass)

def cCompile(givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListC()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    for file in files:
        (_cBase, cFile, cExe) = cFile2Components(file)
        genericCompile(CCOMPILER, CFLAGS + [cExe], cFile, cExe)

def genericRun(vmRunner, vmFlags, exeFile):
    if not os.path.isfile(exeFile):
        return -1
    helperMsg = format("running %s" % (exeFile))
    startHelpSeparator(helperMsg)
    if not os.path.isfile(exeFile):
        print("ALERT: Could not find %s to run" % exeFile)
        return
    if vmRunner is None:
        command = [exeFile]
    else:
        command = [[vmRunner] + vmFlags + [exeFile]]
    result = None
    try:
        result = subprocess.run(command, timeout=TIMEOUT)
    except subprocess.TimeoutExpired as err:
        print("ALERT: Ran out of time when running %s " % command)
        print("ALERT: Possible cause waiting for keyboard input")
        print("ALERT: Possible cause infinite loop")
        print("TimeoutExpired error: {0}".format(err))

    if result is None or result.returncode:
        print("ALERT: Got an error when running %s using %s" % (exeFile, command), flush=True)
    endHelpSeparator(helperMsg)
    return result.returncode

def javaRun(givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirList(".*.class$")
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    for file in files:
        (javaBase, _javaFile, _javaClass) = javaFile2Components(file)
        genericRun(JAVAVM, JAVAFLAGS, javaBase)

def cRun(givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirList(".*.exe$")
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    for file in files:
        (_cBase, _cFile, cExe) = cFile2Components(file)
        genericRun(None, [], "./" + cExe)

def javaCompileRun(file=None):
    javaCompile(file)
    javaRun(file)

def cCompileRun(givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListC()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    for file in files:
        (_cBase, cFile, cExe) = cFile2Components(file)
        cCompile(cFile)
        cRun(cExe)

def javaCleanClassFiles():
    files = dirList(".*.class$")
    for file in files:
        os.unlink(file)

def cCleanExeFiles():
    files = dirList(".*.exe$")
    for file in files:
        os.unlink(file)

def javaRunCompareOutput(templateFile, givenfile=None):
    if not os.path.isfile(templateFile):
        print("SCRIPT ERROR: Could not find template file: %s" % templateFile)
        return
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListJava()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    helperMsg = format("running %s and comparing output to template" % ", ".join(files))
    startHelpSeparator(helperMsg)
    for file in files:
        (javaBase, javaFile, javaClass) = javaFile2Components(file)
        javaCompile(javaFile)
        if os.path.isfile(javaClass):
            ftmp = tempfile.NamedTemporaryFile(delete=False)
            ftmp.close()
            command = [JAVAVM] + JAVAFLAGS + [javaBase]
            with open(ftmp.name, "w") as outfile:
                result = subprocess.call(command, stdout=outfile, stderr=outfile)
                if result != 0:
                    print("ALERT: Got an error when running %s using %s" %
                          (javaBase, command), flush=True)
            compareFiles(ftmp.name, os.path.join(TESTERPATH, templateFile))
            os.unlink(ftmp.name)
            os.unlink(javaClass)
        else:
            print("ALERT: Failed to compile %s, so cannot compare to template" % javaFile)
    endHelpSeparator(helperMsg)


def cRunCompareOutput(templateFile, givenfile=None):
    if not os.path.isfile(templateFile):
        print("SCRIPT ERROR: Could not find template file: %s" % templateFile)
        return
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListC()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    helperMsg = format("running %s and comparing output to template" % ", ".join(files))
    startHelpSeparator(helperMsg)
    for file in files:
        (cBase, cFile, cExe) = cFile2Components(file)
        cCompile(cFile)
        if os.path.isfile(cExe):
            ftmp = tempfile.NamedTemporaryFile(delete=False)
            ftmp.close()
            command = ["./" + cExe]
            with open(ftmp.name, "w") as outfile:
                result = subprocess.call(command, stdout=outfile, stderr=outfile)
                if result != 0:
                    print("ALERT: Got an error when running %s using %s" %
                          (cBase, command), flush=True)
                compareFiles(ftmp.name, os.path.join(TESTERPATH, templateFile))
            os.unlink(ftmp.name)
            os.unlink(cExe)
        else:
            print("ALERT: Failed to compile %s, so cannot compare to template" % cFile)
    endHelpSeparator(helperMsg)

def javaRunWithInput(inputfile, givenfile=None):
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListJava()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    with open(inputfile) as fp:
        lines = fp.readlines()
    helperMsg = format("running %s and feeding it input to examine output" %
                       ", ".join(files))
    startHelpSeparator(helperMsg)
    for file in files:
        (javaBase, javaFile, javaClass) = javaFile2Components(file)
        if not os.path.isfile(javaClass):
            javaCompile(javaFile)
        if os.path.isfile(javaClass):
            helperMsg2 = format("running java %s < %s" % (javaBase, os.path.basename(inputfile)))
            print(helperMsg2)
            print("Input lines are:\n%s" % lines, flush=True)
            with subprocess.Popen([JAVAVM] + JAVAFLAGS + [javaBase], stdin=subprocess.PIPE) as proc:
                proc.stdin.write(bytes("".join(lines), 'utf-8'))
        else:
            print("ALERT: Failed to compile %s, so cannot feed it input to examine output" %
                  javaFile)
    print()
    endHelpSeparator(helperMsg)

def cRunWithInput(inputfile, givenfile=None, outfilefp=None):
    if not os.path.isfile(inputfile):
        print("SCRIPT ERROR: cRunWithInput could not find %s" % inputfile)
        return
    if givenfile is None or (isinstance(givenfile, list) and givenfile == []):
        files = dirListC()
    elif isinstance(givenfile, list):
        files = givenfile
    else:
        files = [givenfile]
    with open(inputfile) as fp:
        lines = fp.readlines()
    helperMsg = format("running %s and feeding it input to examine output" %
                       ", ".join(files))
    startHelpSeparator(helperMsg)
    for file in files:
        (_cBase, cFile, cExe) = cFile2Components(file)
        if not os.path.isfile(cExe):
            cCompile(cFile)
        if os.path.isfile(cExe):
            helperMsg2 = format("running %s < %s" % (cExe, os.path.basename(inputfile)))
            print(helperMsg2)
            print("Input lines are:\n%s" % lines, flush=True)
            if not outfilefp is None:
                with open(outfilefp.name, "w") as outfile:
                    with subprocess.Popen(["./" + cExe],
                                          stdin=subprocess.PIPE,
                                          stdout=outfile,
                                          stderr=outfile) as proc:
                        proc.stdin.write(bytes("".join(lines), 'utf-8'))
                    outfile.write("\n")
            else:
                with subprocess.Popen(["./" + cExe], stdin=subprocess.PIPE) as proc:
                    proc.stdin.write(bytes("".join(lines), 'utf-8'))
        else:
            print("ALERT: Failed to compile %s, so cannot feed it input to examine output" %
                  cFile)
    print()
    endHelpSeparator(helperMsg)

def cRunWithInputOutput(inputfile, templateFile, givenfile):
    if not os.path.isfile(inputfile):
        print("SCRIPT ERROR: cRunWithInput could not find %s" % inputfile)
        return
    if not os.path.isfile(templateFile):
        print("SCRIPT ERROR: cRunWithInput could not find %s" % templateFile)
        return
    outfilefp = tempfile.NamedTemporaryFile(delete=False)
    outfilefp.close()
    cRunWithInput(inputfile, givenfile, outfilefp)
    if os.path.isfile(outfilefp.name):
        compareFiles(outfilefp.name, os.path.join(TESTERPATH, templateFile), "output")
        os.unlink(outfilefp.name)

###########################################################################
# run a script with timeout
###########################################################################

def runHelper(cmd, args=None, timeout=10):
    # if there is a local file or full path given, let it override the directory
    if os.path.isfile(cmd):
        fullcmd = cmd
    else:
        fullcmd = os.path.join(TESTERPATH, cmd)
    if not os.path.isfile(fullcmd):
        print("*** Could not find %s to execute, skipping test" % fullcmd)
        return
    if not os.access(fullcmd, os.X_OK):
        print("*** Cannot execute %s, check file permissions" % fullcmd)
        return
    # print("Running %s" % fullcmd, flush=True)
    if args is None:
        args = []
    runcmd = [fullcmd] + args
    # print(runcmd)
    run = None
    try:
        run = subprocess.run(runcmd, timeout=timeout)
    except subprocess.TimeoutExpired as err:
        print("ALERT: Ran out of time when running %s " % fullcmd)
        print("ALERT: Possible cause waiting for keyboard input")
        print("ALERT: Possible cause infinite loop")
        print("TimeoutExpired error: {0}".format(err))
    if run is None:
        print("ALERT: Did not get to run the command %s " % fullcmd)
    elif run.returncode != 0:
        print("ALERT: Subprocess returned %d for command %s " % (run.returncode, fullcmd))
    # Assume all is well


###########################################################################
# Mail Section
###########################################################################
def mailGetToAddressFromNETID():
    files = os.listdir('.')
    pat = "^tester_netid_(.*).txt$"
    prog = re.compile(pat)
    studentEmail = None
    for file in files:
        result = prog.match(file)
        if result:
            studentEmail = format("%s@uw.edu" % result.group(1))
    # email = 'yusuf.pisan@gmail.com'
    return studentEmail

def mailWriteIntroduction(fp, introFile=None):
    msg = """

Hi,

This is JollyFeedback, but you can call me Jolly. I am an automated script. I ran a bunch of tests on your submission and the result is below. I am not very clever, so I easily get confused when the file names are wrong or when the output does not match what I expected. Still, I work hard! I am getting better.

Hopefully the feedback below will be helpful to you.

Your friendly automated script,

Jolly
PS: If you need to get a hold of my owner, the email address is pisan@uw.edu.
Blame him for all the faults and I will take credit for anything good

"""
    if (not introFile is None) and os.path.isfile(introFile):
        with open(introFile) as introfp:
            msg = "".join(introfp.readlines())
    fp.write(msg)

def mailSMTPLogin(smtpConnection, authFile=None):
    """return 1 for success, -1 for smtp error and 0 for no authorization attempted"""
    smtpuser = None
    smtppass = None
    if os.path.isfile(authFile):
        with open(authFile) as authfp:
            smtpuser = authfp.readline().rstrip()
            smtppass = authfp.readline().rstrip()
        if not smtpuser is None and not smtppass is None:
            try:
                smtpConnection.login(smtpuser, smtppass)
            # pylint: disable=line-too-long
            except (smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError, smtplib.SMTPException) as err:
                print("*** Username/Password was not accepted by SMTP server")
                print("*** The error message was %s" %err)
                return -1
            return 1
    return 0

def mailSendViaSMTP(fromemail, recipents, msg, authfile=None, smtpserver=None):
    smtpConnection = smtplib.SMTP(smtpserver, 587)
    smtpConnection.starttls()
    mailSMTPLogin(smtpConnection, authfile)
    smtpConnection.sendmail(fromemail, recipents, msg)
    smtpConnection.quit()

def hostnameIsValid(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

def emailIsValid(emailAddress):
    emailRegex = "\A[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*" # pylint: disable=anomalous-backslash-in-string
    emailRegex = emailRegex + "@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+" # pylint: disable=anomalous-backslash-in-string
    emailRegex = emailRegex + "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?" # pylint: disable=anomalous-backslash-in-string
    return not emailAddress is None and re.compile(emailRegex).match(emailAddress)

def getFullFromName(fromname, fromEmail):
    if fromname is None:
        return format("<%s>" % (fromEmail))
    return format("%s <%s>" % (fromname, fromEmail))

# pylint: disable=too-many-arguments, too-many-locals
def mailSendFile(fromEmail=None,
                 toEmail=None,
                 subject='Comments from JollyFeedback Automated Script',
                 filetosend='tester_logfile.txt',
                 fromname=None,
                 fileforintrotext=None,
                 authfile='~/private/jollyauth.txt',
                 smtpserver='smtp.uw.edu',
                 filetosaveemail="tester_emailedfile.txt",
                 timedelay=MAILTIMEDELAY, reallysend=False):
    # check fromEmail
    if not emailIsValid(fromEmail):
        print("SCRIPT ERROR: The fromEmail address %s is not valid" % fromEmail)
        return
    # check toEmail
    if toEmail is None:
        toEmail = mailGetToAddressFromNETID()
    if toEmail is None or not emailIsValid(toEmail):
        print("SCRIPT ERROR: The toEmail address %s is not valid" % toEmail)
        return
    # check filetosend
    filetosend = os.path.abspath(os.path.expanduser(filetosend))
    if not os.path.isfile(filetosend):
        print("SCRIPT ERROR: The filetosend %s could not be found" % filetosend)
        return
    # fileforintrotext can be None
    # check authfile
    authfile = os.path.abspath(os.path.expanduser(authfile))
    if not os.path.isfile(authfile):
        print("SCRIPT ERROR: The authfile %s could not be found" % authfile)
        return
    # check smtpserver
    if not hostnameIsValid(smtpserver):
        print("SCRIPT ERROR: The smtpserver %s could not be resolved" % smtpserver)
        return
    # Enough checks, lets do it
    # Read filetosend
    with open(filetosend) as testerlog:
        testerLines = testerlog.read()
    # Prepare saved version of email
    with open(filetosaveemail, "w") as fp:
        mailWriteIntroduction(fp, fileforintrotext)
        startHelpSeparator(format("Sent from %s to %s on %s\n" %
                                  (fromEmail, toEmail, time.strftime("%Y-%m-%d %H:%M:%S"))), fp)
        fp.write(testerLines)
    # Email files saved, open and read it
    with open(filetosaveemail) as fp:
        msgbody = fp.read()
    msg = email.mime.text.MIMEText(msgbody)
    msg['From'] = getFullFromName(fromname, fromEmail)
    msg['To'] = toEmail
    msg['Subject'] = subject
    msg = msg.as_string()
    recipients = [fromEmail, toEmail]
    # CHECK if you REALLY want to send it
    if reallysend:
        helpermsg = format("Sending mail to %s" % toEmail)
        startHelpSeparator(helpermsg)
        print("* Copy of this email is in %s\n===" % filetosaveemail)
        mailSendViaSMTP(fromEmail, recipients, msg, authfile=authfile, smtpserver=smtpserver)
        time.sleep(timedelay)
        endHelpSeparator(helpermsg)
    else:
        helpermsg = "--reallysend is FALSE so not actually sending mail"
        startHelpSeparator(helpermsg)
        print("* Copy of this email is in %s\n===" % filetosaveemail)
        # print(msgbody)
        endHelpSeparator(helpermsg)

if __name__ == "__main__":
    print(HELPERINFO)
