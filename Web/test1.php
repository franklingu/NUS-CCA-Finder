<?php
/*
$temp = new Test;  //this "new" key word seems not to be needed to be deleted manually
echo "Test A: ".Test::$static_property."<br />";
echo "Test B: ".$temp->go_sp()."<br />";
echo "something";
//echo "Test c: ".$temp->$static_property."<br />";

class Test
{
    static $static_property = "I am static";

    public function go_sp()
    {
    	return $static_property;
    }
}
*/
//this piece of code in fact does not work like what is written on the book
//first instance to be noticed

class Father
{
	public function test()
	{
		echo "[father] this is father"."<br />";
	}
}

class Son extends Father
{
	public function test1()
	{
		echo "[Son] this is luke"."<br />";
	}
	public function test2()
	{
		parent::test();
	}
}

$object = new Son;
$object->test1();
$object->test2();

$paper = array('copier' => "copier & multipurpose",
	           'inkjet' => "inkjet printer",
	           'laser' => "laser printer",
	           'photo' => "photocopy");

foreach ($paper as $item => $name) {
	echo "$item: $name<br />";
}

?>