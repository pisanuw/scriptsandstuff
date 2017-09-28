
A php based program to see student pictures, choose a random student,
and choose a random student without showing name to help instructors
learn students' names

The index.php file is placed in ~/public_html/students/ on homer

For each course, there is a separate directory, such as 111, Inside
the directory is a set of jpeg files of the format
FIRSTNAME_LASTNAME.jpeg. The program uses the file names to figure out
the class list. To add a new student, add a jpeg file to the directory.

Since we do not want anybody on the web accessing student names and
pictures, place a .htaccess file in ~/public_html/students/

.htaccess file looks like this

AuthType UWNetID
PubcookieAppID "MyApplication"
require user pisan

Assumptions: Many. This works on homer.u.washington.edu but not
guaranteed to work on other systems. The images are assumed to be
150x120 which is what UW system has for student images. Assuming no
spaces in directories or files or anything funny in the URL.

Last Updated: 2017-09-28
Author: pisan@uw.edu
