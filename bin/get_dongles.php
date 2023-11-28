<?php
echo "<PRE>";

# Array of supported HW devices
$vidpid = array(0 => '0bda:2838', 
				1 => '0ccd:00a9',
				2 => '0ccd:00b3',
				3 => '0ccd:00d3',
				4 => '0ccd:00e0',
				5 => '185b:0620',
				6 => '185b:0650',
				7 => '1f4d:b803',
				8 => '1f4d:c803',
				9 => '1b80:d3a4',
				10 => '1d19:1101',
				11 => '1d19:1102',
				12 => '1d19:1103',
				13 => '0458:707f',
				14 => '1b80:d393',
				15 => '1b80:d394',
				16 => '1b80:d395',
				17 => '1b80:d39d'
				);

# get full lsusb
system("lsusb >/tmp/dvb-dongle_full.txt");
# filter Dongels by VIDPID array for RTL supported
foreach ($vidpid as $key)    {
	system("sed -n '/".$key."/p' /tmp/dvb-dongle_full.txt >> /tmp/dvb-dongle.txt");
}
# filter Serial by VIDPID array
foreach ($vidpid as $key)    {
	system("lsusb -d ".$key." -v | grep Serial >> /tmp/test.txt");
}

$dongles = array();
$test = explode("\n", file_get_contents('/tmp/dvb-dongle.txt'));
foreach($test as $line) {
  if(!empty($line))
    #echo $line;
	array_push($dongles,$line);
}
#print_r($dongles);

$file = file_get_contents('/tmp/test.txt');
$words = preg_split("#\r?\n#", $file, -1, PREG_SPLIT_NO_EMPTY);
$serial = array();
foreach ($words as $key)    {
	preg_match('/[0-9]{6,8}/',$key, $matches);
	array_push($serial,$matches[0]);
}
#print_r($serial);

$final = array();
$combine = array_combine($serial, $dongles);
file_put_contents('/tmp/final_dongles.txt', json_encode($combine, JSON_PRETTY_PRINT));

unlink("/tmp/test.txt");
unlink("/tmp/dvb-dongle_full.txt");
unlink("/tmp/dvb-dongle.txt");
print_r($combine);




?>