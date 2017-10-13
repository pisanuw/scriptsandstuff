#!/usr/local/bin/python3


import argparse
from subprocess import Popen, PIPE
import socket
import datetime
import re
import os
import time
import smtplib
from email.mime.text import MIMEText


# must specifcy --sendemail on command line to actually send email
# see other arguments below

def intro(fp):
    msg = """

Hi,

This is JollyFeedback, but you can call me Jolly. I am an automated script. I ran a bunch of tests on your submission and the result is below. I am not very clever, so I easily get confused when the file names are wrong or when the output does not match what I expected. Still, I work hard! I am getting better.

Hopefully the feedback below will be helpful to you.

Your friendly automated script,

Jolly
PS: If you need to get a hold of my owner, the email address is pisan@uw.edu.
Blame him for all the faults and I will take credit for anything good

"""
    if args.fileforintrotext:
        with open(args.fileforintrotext) as introfp:
            msg = "".join(introfp.readlines())
    fp.write(msg)
    
def smtpAuth(smtp):
    smtpuser = ""
    smtppass = ""
    if args.smtpauthfile and os.path.isfile(args.smtpauthfile):
        with open(args.smtpauthfile) as s:
            smtpuser = s.readline().rstrip()
            smtppass = s.readline().rstrip()
        if smtpuser != "" and smtppass != "":
            try:
                # print("U: %s, P: %s" % (smtpuser, smtppass))
                smtp.login(smtpuser, smtppass)
            except (smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError, smtplib.SMTPException) as err:
                print("*** Username/Password was not accepted by SMTP server")
                print("*** The error message was %s" %err)
                exit(-1)
            
def sendAuthenticatedMail(to, msgbody):
    msg = MIMEText(msgbody)
    toAll = [ 'pisan@uw.edu' , to ]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg['Subject'] = args.subject
    if (args.fromname != ""):
        fullfromname = format("%s <%s>" % (args.fromname, args.fromemail))
    else:
        fullfromname = format("<%s>" % (args.fromemail))
    msg['From'] = fullfromname
    msg['To'] = to
    s = smtplib.SMTP(args.smtp, 587)
    s.starttls()
    smtpAuth(s)
    s.sendmail(args.fromemail, toAll, msg.as_string())

    
def sendFileViaMail(toEmail, textfile):
    emailFile = args.filetosaveemail;
    with open(emailFile, "w") as fp:
        intro(fp)
        fp.write("\n\n========================================\n")
        fp.write("Sent from %s to %s on %s\n" %(args.fromemail, toEmail, time.strftime("%Y-%m-%d %H:%M:%S")))
        with open(textfile) as testerlog:
            lines = testerlog.read()
        fp.write(lines)
        
    with open(emailFile) as fp:
        msgLines = fp.read()

    if (args.sendemail):
        print("\n\n========================================")        
        print("Sending mail to %s" % toEmail)
        sendAuthenticatedMail(toEmail, msgLines)
        time.sleep(args.timedelay)
        print("Mail successfully sent")
        print("========================================\n")                
    else:
        print("--sendemail flag was not passed so not sending mail")
        print("The email message would have been: \n")
        print("===========START EMAIL MESSAGE=======================================", flush=True)
        if (args.fromname != ""):
            fullfromname = format("%s <%s>" % (args.fromname, args.fromemail))
        else:
            fullfromname = format("<%s>" % (args.fromemail))
        print("From: %s" % fullfromname)
        print("To: %s" % toEmail)
        print("Subject: %s" % args.subject)
        print(msgLines)
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



parser = argparse.ArgumentParser()
parser.add_argument("--sendemail", help="must be specified to really send email", action='store_true')
parser.add_argument("--fromemail", help='From address in the form of xxx@yyy.edu', required=True)
parser.add_argument("--subject", default='Comments from JollyFeedback Automated Script', help='Subject: line (default: %(default)s)')
parser.add_argument("--smtp", default='smtp.uw.edu', help='smtp server to use (default: %(default)s)')
parser.add_argument("--timedelay", default=15, type=int, help='seconds to wait between emails (default: %(default)s)')
parser.add_argument("--smtpauthfile", help='username and password for smtp authentication')
parser.add_argument("--filetosend", default='tester_logfile.txt', help='the log file to send (default: %(default)s)')
parser.add_argument("--filetosaveemail", default='tester_emailedfiled.txt', help='save a copy of the email sent in (default: %(default)s)')
parser.add_argument("--fileforintrotext", default='Some long text, see source file', help='friendly text about the script, default: %(default)s)')
parser.add_argument("--fromname", default="", help='actual name such as "Cris Doe"')

# can also use %(prog) for the name of program
args = parser.parse_args()

# Check that email is valid
emailRegex = "\A[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
prog = re.compile(emailRegex)
result = prog.match(args.fromemail)
if not result:
    print("The email address %s is not valid" % args.fromemail)
    exit(-1)
                                                  
if not os.path.isfile(args.filetosend):
    print("Could not find filetosend, was looking for %s" % args.filetosend)
    exit(-1)

if args.fileforintrotext:
    args.fileforintrotext = os.path.abspath(os.path.expanduser(args.fileforintrotext))
    if not os.path.isfile(args.fileforintrotext):
        print("Could not find fileforintrotext, was looking for %s" % args.fileforintrotext)
        exit(-1)

if args.smtpauthfile:
    args.smtpauthfile = os.path.abspath(os.path.expanduser(args.smtpauthfile))
    if not os.path.isfile(args.smtpauthfile):
        print("Could not find smtpauthfile, was looking for %s" % args.smtpauthfile)
        exit(-1)    
    

# print("Netid is %s" % getNetIDfromFile())
netid = getNetIDfromFile()

if not netid:
    print("Could not find netid for sending emails, it should be in file tester_netid_xxx where xxx is netid")
    exit(-1)
else:
    toEmail = format("%s@uw.edu" % netid)

# This is for testing, send emails to this address
# rather than the actual netid based address
# toEmail = "yusuf.pisan@gmail.com"


sendFileViaMail(toEmail, args.filetosend)

    
exit(0)

