<!DOCTYPE html>
<html>
<head>
  <title>Students</title>
</head>
<body>

<?php

$baseURL = strtok($_SERVER["REQUEST_URI"],'?');

print("<h1><a href=\"$baseURL\">Students</a></h1>\n");


function noDots($f) {
   return ! preg_match('/^\./', $f);
}

function file2name($f) {
   $result = preg_match('/^(.*)_(.*).jpeg$/', $f, $matches);
   if ($result) {
       return array($matches[1], $matches[2]);
   } else {
       return array("NOFirstName", "BADFileNAme");
   }
}
function studentTable($dir, $n) {
   list($first, $last) = file2name($n);
   print("<table style=\"display:inline\"><tr><td><img height=\"150\" width=\"120\" alt=\"$n\" ");
   print("src=\"" . $dir . "/" . $n . "\"></img>");
   print("<div>$first $last</div> </td></tr></table>\n");
}

function studentFiles($dir) {
   return array_filter(scandir($dir), "noDots");
}

function face2Name($dir) {
   $classURL = "?class=$dir";
   print("<h2>Random Student from <a href=\"$classURL\">$dir</a></h2>\n");
   $randomURL = "?class=$dir&c=2";
   print("<p>Pick another <a href=\"$randomURL\">random student no name</a></p>\n");
   $students = studentFiles($dir);
   $n = array_rand($students);
   list($first, $last) = file2name($students[$n]);
   print("<table style=\"display:inline\"><tr><td><img height=\"150\" width=\"120\" alt=\"$n\" ");
   print("src=\"" . $dir . "/" . $students[$n] . "\"></img>");
   print("</td></tr></table>\n");
   print("<p id=\"hiddenname\" style=\"display:none\">$first $last</p> ");
   print("<p></p><button type=\"button\" ");
   print("onclick=\"document.getElementById('hiddenname').style.display='block'\">Show it!</button>\n");
   
}

function randomStudent($dir) {
   $classURL = "?class=$dir";
   print("<h2>Random Student from <a href=\"$classURL\">$dir</a></h2>\n");
   $randomURL = "?class=$dir&c=1";
   print("<p>Pick another <a href=\"$randomURL\">random student</a></p>\n");
   $students = studentFiles($dir);
   $n = array_rand($students);
   studentTable($dir, $students[$n]);
}

function allStudents($dir) {
   $students = studentFiles($dir);
   $lx = count($students);
   print("<h2>$lx students in $dir</h2>\n");
   $randomURL = "?class=$dir&c=1";
   $randomURL2 = "?class=$dir&c=2";
   print("<p>Pick a <a href=\"$randomURL\">random student</a></p>\n");
   print("<p>Pick a <a href=\"$randomURL2\">random student no name</a></p>\n");
   print("<div id=\"students\">\n");
   foreach ($students as $s) {
          studentTable($dir, $s);
   }
   print("</div>\n");
}
?>
<!-- If no class given, display possible classes -->
<?php
   $class = $_GET['class'];
   $choice = $_GET['c'];
   if (($class == "") || !is_dir($class)) {
      $dirs = array_filter(scandir('.'), "noDots");
      print("<ul>\n");
      foreach ($dirs as $d) {
          if (is_dir($d)) {
              $url = "?class=$d";
              $url_random = "?class=$d&c=1";
              $url_random2 = "?class=$d&c=2";
              print("<li><a href=\"$url\">$d</a> \n");
              print("<a href=\"$url_random\">(random)</a> \n");
              print("<a href=\"$url_random2\">(random no name)</a> </li>\n");
          }
      }
      print("</ul>\n");
   } elseif ($choice == "") {
      allStudents($class);
   } elseif ($choice == "1") {
      randomStudent($class);
   } elseif ($choice == "2") {
      face2Name($class);
   } else {
      print("<h2>Hmm, did not expect to get here!</h2>\n");
   }
?>

</body>
</html>
