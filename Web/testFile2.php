<?php
$fh = fopen('testfile.txt', 'r') or die("Could not open the file");

$line = fgets($fh);
fclose($fh);
echo $line;
echo "<br /> "; //why cannot i use $line+""???

copy('testfile.txt', 'testfile2.txt') or die("Could not copy the file");
echo "file is successfully copied";

rename('testfile2.txt', 'testfile2.in') or die("cannot rename it");
echo "then the file is renamed to 'testfile2.in'";
?>