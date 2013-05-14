<?php //upload files
if ($_FILES)
{
	$name = $_FILES['filename']['name'];

	switch ($_FILES['filename']['type']) {
		case 'image/jpeg':
			$ext = 'jpg';
			break;
		case 'image/gif':
		    $ext = 'gif';
		    break;
		case 'image/png':
		    $ext = 'png';
		    break;
		case 'image/png':
		    $ext = 'png';
		    break;
		case 'image/tiff':
		    $ext = 'tif';
		    break;
		
		default:
			$ext = '';
			break;
	} //this block of code does work
	if ($ext)
	{
		$name="image.$ext";
        move_uploaded_file($_FILES['filename']['tmp_name'], $name);
        echo "upload file: '$name'<br />";
	}
	else echo "Wrong format";
}
else echo "No image is selected <br />";
?>