#!/usr/bin/env php
<?php

require_once "loxberry_system.php";
require_once "loxberry_log.php";
require_once "loxberry_io.php";
require_once "phpMQTT/phpMQTT.php";


$configfile	= "config.json";
$rtl_433_configfile	= "rtl_433.conf";

echo "<PRE>";

# load Plugin Configuration
if (file_exists($lbpconfigdir . "/" . $configfile))    {
	$config = json_decode(file_get_contents($lbpconfigdir . "/" . $configfile), TRUE);
} else {
	echo "The configuration file could not be loaded, the file may be disrupted. We have to abort :-(')".PHP_EOL;
	exit;
}

#print_r($config);

# Explore Protocols
$prot = explode(':',$config['DONGLE1']['protocols']);
# check if entries exists;
$containsEmpty = in_array("", $prot);

# load MQTT Details
$creds = mqtt_connectiondetails();

// MQTT requires a unique client id
$client_id = uniqid(gethostname()."_client");
$mqtt = new Bluerhinos\phpMQTT($creds['brokerhost'],  $creds['brokerport'], $client_id);
$mqtt->connect(true, NULL, $creds['brokeruser'], $creds['brokerpass']);
#print_r($creds);

$heute = date("d.m.Y"); 
$time = date("G:i"); 

$level = LBSystem::pluginloglevel();
#print_r($level);

###########################################################
# Start writing rtl_433 config file
###########################################################
$file = fopen("$lbpconfigdir/$rtl_433_configfile","w",1);
	fwrite($file,"# config for rtl_433\r\n");
	fwrite($file,"# created on ".$heute." at ".$time."h\r\n");
	fwrite($file,"\r\n");
	# If loglevel = 3 then error mode
	if ($level == 3)  {
		fwrite($file,"verbose 3\r\n");
	}
	# If loglevel = 4 then warning mode
	if ($level == 4)  {
		fwrite($file,"verbose 4\r\n");
	}
	# If loglevel = 6 then info/notice mode
	if ($level == 6)  {
		fwrite($file,"verbose 5\r\n");
		fwrite($file,"verbose 6\r\n");
	}
	# If loglevel = 7 then debug/trace mode
	if ($level == 7)  {
		fwrite($file,"verbose 7\r\n");
		fwrite($file,"verbose 8\r\n");
	}
	fwrite($file,"device :".trim($config['DONGLE1']['Serial']??'')."\r\n");
	fwrite($file,"frequency ".$config['DONGLE1']['freq1']."\r\n");
	# Check for other Frequences entered
	if ($config['DONGLE1']['freq2'] != "0")  {
		fwrite($file,"frequency ".$config['DONGLE1']['freq2']."\r\n");
		$hopp = "1";
	} 
	if ($config['DONGLE1']['freq3'] != "0")  {
		fwrite($file,"frequency ".$config['DONGLE1']['freq3']."\r\n");
		$hopp = "1";
	} 
	if ($config['DONGLE1']['freq4'] != "0" and !empty($config['DONGLE1']['freq4']))  {
		$len = strlen($config['DONGLE1']['freq4']);
		if ($len === 9)   {
			fwrite($file,"frequency ".$config['DONGLE1']['freq4']."\r\n");
		} else {
			fwrite($file,"frequency ".$config['DONGLE1']['freq4']."M\r\n");
		}
		$hopp = "1";
	}
	# If more then one frequence entered add hop interval
	if ($hopp == "1")  {
		if (!empty($config['DONGLE1']['hop']))  {
			fwrite($file,"hop_interval ".$config['DONGLE1']['hop']."\r\n");
		# If hop interval not been entered set default to 60
		} else {
			fwrite($file,"hop_interval 60\r\n");
		}
	}
	# If dedicated Protocols were selected
	if (!$containsEmpty)   {
		foreach ($prot as $item)  {
			fwrite($file,"protocol ".$item."\r\n");
		}
	}
	#fwrite($file,"gain 0\r\n");
	fwrite($file,"convert si\r\n");
	fwrite($file,"sample_rate ".$config['DONGLE1']['sample']."\r\n");
	#fwrite($file,"ppm_error 0\r\n");
	#fwrite($file,"samples_to_read 0\r\n");
	#fwrite($file,"analyze_pulses false\r\n");
	fwrite($file,"report_meta time:unix\r\n");
	fwrite($file,"report_meta protocol\r\n");
	fwrite($file,"report_meta noise\r\n");
	fwrite($file,"report_meta level\r\n");
	fwrite($file,"pulse_detect autolevel\r\n");
	#fwrite($file,"signal_grabber none\r\n");
	# MQTT Credentials and output
	fwrite($file,"output mqtt://".$creds['brokeraddress'].",user=".$creds['brokeruser'].",pass=".$creds['brokerpass'].",retain=0,devices=rtl_433[/protocol][/model][/id]\r\n");
	# path to Log file
	fwrite($file,"output log:".$lbplogdir."/rscan4lox.log\r\n");
	fwrite($file,"stop_after_successful_events false\r\n");
fclose($file);
?>
