<?php
$cmd = "dir";

exec(escapeshellcmd($cmd),$output,$status);

if ($status) {
	echo "execution failed";
}
else{
	echo "<pre>";
	foreach ($output as $line) {
		echo "$line\n";
	}
}

?>