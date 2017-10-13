#!/usr/local/bin/python3

from subprocess import Popen, PIPE
import socket
import datetime
import re
import os
import time


runningOn = socket.gethostname()

SENDMAIL = True;

officepat = "MAC-30223656"
prog = re.compile(officepat)
isOffice = (prog.match(runningOn) != None)

fromEmail = 'pisan@uw.edu'
fromHeader = format("Yusuf Pisan <%s>" % fromEmail)
subjectHeader = 'CSS 132: Feedback via JollyFeedback Automated Script'

def intro(fp):
    fp.write("\nHi,\n\n")
    fp.write("This is JollyFeedback, but you can call me Jolly. I am an automated script. ");
    fp.write("I ran a bunch of tests on your submission and the result is below. ");
    fp.write("I am not very clever, so I easily get confused when the file names are wrong ")
    fp.write("or when the output does not match what I expected. Still, I work hard! I am getting better. ")
    fp.write("\n\nHopefully the feedback below will be helpful to you.")
    fp.write("\n\nYour friendly automated script,")
    fp.write("\n\nJolly")
    fp.write("\n\nPS: If you need to get a hold of my owner, the email address is pisan@uw.edu.")
    fp.write("\nBlame him for all the faults and I will take credit for anything good\n\n")
    fp.write("===============================\n")
    
           


def sendMail(toEmail, textfile):
    emailFile = "tester_toemail.txt"
    with open(emailFile, "w") as fp:
        intro(fp)
        fp.write("\nSent at: " +  time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        with open(textfile) as testerlog:
            lines = testerlog.read()
        fp.write(lines)
        
    with open(emailFile) as fp:
        txtfile = fp.read()

    msg = format("From: %s\nTo: %s\nSubject: %s\n\n%s\n" % (fromHeader, toEmail, subjectHeader, txtfile))
    if (SENDMAIL and isOffice):
        print("Sending mail to %s" % toEmail)
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi", toEmail, fromEmail] , stdin=PIPE)
        p.communicate(msg.encode())
    else:
        print("SENDMAIL is set to %s and running on %s so not sending mail" % (SENDMAIL, runningOn))
        print("The email message would have been: \n")
    print("===========START EMAIL MESSAGE=======================================", flush=True)
    print(msg)
    print("===========END EMAIL MESSAGE=======================================", flush=True)    

def getNetIDfromFile():
    files = os.listdir('.')
    pat = "^tester_netid_(.*)\.txt$"
    prog = re.compile(pat)
    for f in files:
        result = prog.match(f)
        if result:
            return result.group(1)
    return 0


# print("Netid is %s" % getNetIDfromFile())
netid = getNetIDfromFile()
if netid:
    # toEmail = format("%s@uw.edu" % netid)
    toEmail = "yusuf.pisan@gmail.com"
    sendMail(toEmail, "tester_logfile.txt")
    
# sendMail("sample.txt")
exit(0)

