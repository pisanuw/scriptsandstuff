#!/usr/bin/env python
"""Check Style"""

import re
import os
import sys

fileLines = []
WARNINGS = {}

REGEXoperatorSpace = re.compile("(\w(\+|\-|\*|\<|\>|\=)\w)" + "|(\w(\=\=|\<\=|\>\=)\w)")
REGEXoperatorSpacestr = "[PUT SPACE AROUND OPERATORS]"

REGEXfor = re.compile('for\s*\(')
REGEXint = re.compile("int ")
REGEXvoid = re.compile("void ")
REGEXdouble = re.compile("double ")

# inlcude line without space
# #include<stdio.h>
REGEXincludeNeedsSpace = re.compile("^#include<")
REGEXincludeNeedsSpacestr = "[SPACE AFTER INCLUDE]"

# commented out code
#  //printf(".");
REGEXcommentedPrintf = re.compile("//\s*printf\s*\(")
REGEXcommentedPrintfstr = "[REMOVE UNUSED CODE]"

# for loop without int inside
# for(i = 1; i 
# for (dots = norows - row
def ruleForShouldHaveInt(lineNumber, line):
    if re.search(REGEXfor, line):
        if not re.search(REGEXint, line):
            addWarning(lineNumber, "[FOR LOOPS USUALLY HAVE A VARIABLE WITH int DEFINED]")
            
# condition with unnecessary casting
# if((int)(j/5) == 3)




# no space between #include and code
#include <stdlib.h>
# void printStar(int count){

# no space between ) and {
# ){

# inside a for loop use shortcut
# middle = middle -1)

# inside for loop operator balanced on both sides
# middle = middle -1)

# space between operators
# (size-1)/4
# int numDots = (size - numStars)/2;
#  (i <=a)
# x<=i 
# (y%2 ==1)
# f<star

# unnecessary commenting
# //Print Star "*" based on given parameter.
#   printf("*");
# //Print Stars
#       printStar(numStars);
    
# empty line after function def
# void dot (int n)
# 
# {
# after for
#for(i = 1; i <= n; i ++)
#
#    {
   
# for loop no indent
#   for (int i = 0; i < s; i++ )
#    printf("."); 
#      for (int dot = x; dot <= size / 2; dot++)
#    {

# no indent after {
#{
#int 
    
# if with no body
# if (size%2==1);

# no space before ;
# size -=2 ;

# comments not in line with code
##// we can only do odd size arrows
##    assert(size % 2 == 1);

# read given file
def readFile(fname):
    global fileLines
    with open(fname, "r") as fp:
        lines = fp.read().splitlines()
    fileLines = ["***** This is a placeholder line so file line numbers match array index *****"] + lines
        
def getFileLine(i):
    return format("%s %s" % ('{0:<5}'.format(i), fileLines[i]))
# read given file
def displayFile():
    for i in range(1, len(fileLines)):
        # print("Line %s" % i)
        if i in WARNINGS:
            # print("WARN is %s" % WARNINGS[i])
            for warning in WARNINGS[i]:
                print(warning)
        print(getFileLine(i))

def addWarning(i, msg):
    # print("---> WARN %s %s" % (i, msg))
    if i in WARNINGS:
        WARNINGS[i].append(msg)
    else:
        WARNINGS[i] = [msg]

def ruleSimpleSingleLine(lineNumber, line, regex, msg):
    if regex.search(line):
        addWarning(lineNumber, msg)




def singleLineRules():
    for i in range(1, len(fileLines)):
        line = fileLines[i]
        ruleSimpleSingleLine(i, line, REGEXoperatorSpace, REGEXoperatorSpacestr)
        ruleSimpleSingleLine(i, line, REGEXincludeNeedsSpace, REGEXincludeNeedsSpacestr)
        ruleSimpleSingleLine(i, line, REGEXcommentedPrintf, REGEXcommentedPrintfstr)
        
        
        ruleForShouldHaveInt(i, line)
        
    
if len(sys.argv) > 1:
    userFile = sys.argv[1]
else:
    userFile = "coffeeorder.c"
    
if not os.path.isfile(userFile):
    print("SCRIPT ERROR: Could not find the file to read: %s" % userFile)
readFile(userFile)
singleLineRules()
displayFile()

print("Done.")
