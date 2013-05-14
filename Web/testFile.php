<?php
$fh = fopen("testfile.txt","w") or die("Failed to create the file");
$text = <<<_END
Line1
Line2
Line3
_END;
fwrite($fh,$text) or die("Could not write to the file");
fclose($fh);
echo "File 'testfile.txt' written successfully!";
?>