#!/usr/bin/env python

##################################################
# NOT WORKING
# Canvas requires downloading each submission separately via API
# Downloading each one, making sure they are the latest version
# putting them into a directory is not worth the time saved!
##################################################
# valid https://canvas.uw.edu/api/v1/courses?per_page=100&page=1

import json
import urllib.parse
import urllib.request
import shutil
import os
import stat
import hashlib
import re
import argparse

ALLCOURSES = []
ALLASSIGNMENTS = []

class Course():
    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name
    def __str__(self):
        return "<C: " + str(self.code) + ">"

class Assignment():
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url        
    def __str__(self):
        return "<A: " + str(self.name) + ">"
    
def prettyPrint(data):
    print(json.dumps(data, sort_keys=True, indent=4))

def printCourseIds(courses):
    for i in courses:
        print("%10s \"%s\""%(str(i['id']), i['name']))
            
CANVASAPI = "https://canvas.uw.edu/api/v1/"
CANVASTOKEN = "10~PPkgb80PMrql3qNm3jnAVDDQii1q5ISDtQZeOmMbynj24O1eeLIghJ9Myds1BBJc"

SINGLEPAGE = urllib.parse.urlencode({"per_page":"100", "page": "1"})

def urlRequest(url):
    urlString = CANVASAPI + url
    print("Requesting: %s" % urlString)
    request = urllib.request.Request(urlString)
    request.add_header("Authorization", "Bearer " + CANVASTOKEN);
    response = urllib.request.urlopen(request)
    json_string = response.read().decode('utf-8');
    return json.loads(json_string)

# https://canvas.uw.edu/api/v1/courses?per_page=100&page=1
def getCourses():
    courses = urlRequest("courses?" + SINGLEPAGE)
    for course in courses:
        ALLCOURSES.append(Course(course['id'], course['course_code'], course['name']))

# https://canvas.uw.edu/api/v1/courses/1175454/assignments?per_page=100&page=1
def getAssignments():
    courseID = "1175454"
    assignments = urlRequest("courses/" + courseID + "/" + "assignments?" + SINGLEPAGE)
    for ass in assignments:
        ALLASSIGNMENTS.append(Assignment(ass['id'], ass['name'], ass['submissions_download_url']))
        print(str(ass['id']) + "  " + ass['name'] + "  " + ass['submissions_download_url'])


# UpArrow https://canvas.uw.edu/courses/1175454/assignments/3836800/submissions?zip=1
# https://canvas.uw.edu/api/v1/courses/1175454/assignments?per_page=100&page=1

# single submission based on user_id
# GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

# user_id = 3729515
# https://canvas.uw.edu/api/v1/courses/1175454/assignments/3836801/submissions/3729515

indivAss = "courses/1175454/assignments/3836801/submissions/3729515"
downloaded = urlRequest(indivAss)
prettyPrint(downloaded)

# getCourses()
# getAssignments()
# courseID = "1175454"        
# assignmentID = "3836801"

# commonargs = "&grouped=true&include[]=submission_history&student_ids[]=all&"
# commonargs += SINGLEPAGE

# download = urlRequest("courses/" + courseID +
#                           "/students/submissions?assignment_ids[]=" +
#                           assignmentID + commonargs)

# prettyPrint(download)
# urllib.request.urlretrieve(attachment['url'], directory+"/"+login+exten)

# print(retVal)

