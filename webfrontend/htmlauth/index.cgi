#!/usr/bin/perl -w

# Copyright 2023 Oliver Lewald, olewald64@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


##########################################################################
# Modules
##########################################################################

use CGI;
use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
use LoxBerry::IO;
use LoxBerry::JSON;
use warnings;
#use strict;
use diagnostics;
use Data::Dumper;

##########################################################################
# Generic exception handler
##########################################################################

# Every non-handled exceptions sets the @reason variable that can
# be written to the logfile in the END function

#$SIG{__DIE__} = sub { our @reason = @_ };

##########################################################################
# Variables
##########################################################################

our $template;
our $navbar;
our $lbptemplatedir;
our $content;
our %navbar;
our $SerialNo;
our $templatefile = "index.html";
our $tmp_log_file = "/tmp/scan4lox_log.tmp";
our $resp;
our $jsonobj;
our $pluginconfigjsonfile = "config.json";
my $pluginlogfile = "rscan4lox.log";
my $error_message = "";
my $helplink;
my $helptemplate;
our $log = LoxBerry::Log->new ( name => 'Radioscanner UI', filename => $lbplogdir ."/". $pluginlogfile, append => 1, addtime => 1 );
our $plugin = LoxBerry::System::plugindata();

my $jsonobj = LoxBerry::JSON->new();
our $cfg = $jsonobj->open(filename => $lbpconfigdir . "/" . $pluginconfigjsonfile, writeonclose => 0);


##########################################################################
# Read Settings
##########################################################################

# Read Plugin Version
our $version = LoxBerry::System::pluginversion();

# IP-Address
my $myip =  LoxBerry::System::get_localip();

# Get MQTT Credentials
my $mqttcred = LoxBerry::IO::mqtt_connectiondetails();

# read all POST-Parameter in namespace "R".
our $cgi = CGI->new;
$cgi->import_names('R');


#########################################################################
## Handle ajax requests 
#########################################################################

our $q = $cgi->Vars;
my %pids;

if( $q->{ajax} ) 
{
	my %response;
	ajax_header();
	if( $q->{ajax} eq "getpids" ) {
		pids();
		$response{pids} = \%pids;
		print JSON::encode_json(\%response);
	}
	exit;
}

if( $q->{action} ) 
{
	ajax_header_text();
	if( $q->{action} eq "create_serial" ) {
		$SerialNo = $q->{'Serial'};
		our $No = $q->{'DNumber'};
		change_serial();
		print $resp;
		&form;
	}
	exit;
}

##########################################################################
# Initiate Main Template
##########################################################################
inittemplate();


##########################################################################
# Set LoxBerry SDK to debug in plugin 
##########################################################################

if($log->loglevel() eq "7") {
	$LoxBerry::System::DEBUG 	= 1;
	$LoxBerry::Web::DEBUG 		= 1;
	$LoxBerry::Log::DEBUG		= 1;
	$LoxBerry::JSON::DEBUG		= 1;
	$LoxBerry::JSON::DUMP 		= 1;
}

# übergibt Plugin Verzeichnis an HTML
$template->param("PLUGINDIR" => $lbpplugindir);
$template->param("CONFIGDIR" => $lbpconfigdir);

LOGSTART "Radioscanner";


##########################################################################
# Main program
##########################################################################

# check if Loglevel has been changed
my $act_level = LoxBerry::System::pluginloglevel();
our $oldlog;
if (-e $tmp_log_file) {
	open(FH, '<', $tmp_log_file) or die $!;
	while(<FH>){
		$oldlog = $_;
	}
	if ($oldlog ne $act_level)   {
		unlink($tmp_log_file);
		open(FH, '>', $tmp_log_file) or die $!;
		print FH $act_level;
		&rtl_433_form;
	}
} else {
	open(FH, '>', $tmp_log_file) or die $!;
	print FH $act_level;
}
close(FH);

# detect and list SDR Dongles
our $count;
our $line_sn;
our $list;
my $dongle_list;
my $counter;
my $file = '/tmp/final_dongles.txt';
my @list;
 
my $fileexe = qx(/usr/bin/php $lbpbindir/get_dongles.php);
my $json = LoxBerry::JSON->new();
$list = $json->open(filename => $file, readonly => 1);

if (ref($list) eq "HASH") {
	$count = scalar(%list);
    foreach my $key (keys %$list) {
		$counter++;
		my $countd = $counter -1;
		$dongle_list .= '<b>#<font color="blue">'.$countd .'</font></b>: '. $list->{$key} .' Serial: <b><font color="blue">'. $key. '</font></b><br>';
		$cfg->{"DONGLE".$counter}->{Serial} = $key;
		$cfg->{"DONGLE".$counter}->{Number} = $countd;
		$jsonobj->write();
	}
	# count dongles and push to Template
	$count = %$list;
	$count =~ s/(\r?\n|\r\n?)+$//;
	$cfg->{"DONGLE"}->{count} = $count;
	$jsonobj->write();
	$template->param("USB_LIST", $dongle_list);
} else {
    $dongle_list = "****** No RTL-SDR compatible DVB-T Dongles detected ******";
	# count dongles and push to Template
	$template->param("USB_LIST", $dongle_list);
	$count = 1;
	$cfg->{"DONGLE"}->{count} = $count;
	$jsonobj->write();
}
	
# create array of Sensors/Protocols
my $rowprotocols;
my $protocolfile = "$lbpconfigdir/protocols/rtl_433_protocols.json";
	
my $jsonparse = LoxBerry::JSON->new();
$list = $jsonparse->open(filename => $protocolfile, readonly => 1);
my @array = @{[ @$list ]};


# Create Navbars
$navbar{1}{Name} = "$L{'BASIS.MENU_SETTINGS'}";
$navbar{1}{URL} = './index.cgi';
$navbar{2}{Name} = "$L{'BASIS.MENU_SCANNER'}";
$navbar{2}{URL} = './index.cgi?do=scanner';
$navbar{99}{Name} = "$L{'BASIS.MENU_LOGFILES'}";
$navbar{99}{URL} = './index.cgi?do=logfiles';

if ($mqttcred)  {
	$navbar{3}{Name} = "$L{'BASIS.MENU_MQTT'}";
	$navbar{3}{URL} = '/admin/system/mqtt-finder.cgi?q=rtl_433';
	$navbar{3}{target} = '_blank';
}

if ($R::saveformdata1) {
	$template->param( FORMNO => 'form' );
	&save;
}

if(!defined $R::do or $R::do eq "form") {
	$navbar{1}{active} = 1;
	$template->param("FORM", "1");
	&form;
} elsif ($R::do eq "restart") {
	$template->param("FORM", "1");
	system("sudo systemctl restart rtl_433-mqtt.service");
	LOGINF "Scanner Service restarted";
	printtemplate();
} elsif ($R::do eq "logfiles") {
	LOGTITLE "Show logfiles";
	$navbar{99}{active} = 1;
	$template->param("LOGFILES", "1");
	$template->param("LOGLIST_HTML", LoxBerry::Web::loglist_html());
	printtemplate();
} elsif ($R::do eq "scanner") {
	LOGTITLE "Scanner";
	$navbar{2}{active} = 1;
	$template->param("SCANNER", "1");
	if ( begins_with(LoxBerry::System::lbversion(), '3' ) ) {
		$template->param("LB3", "1");
	}
	printtemplate();
}

$error_message = "Invalid do parameter: ".$R::do;
&error;
exit;


#####################################################
# Form-Sub
#####################################################

sub form 
{	
	# Sensors
	my $sensors;
	my $checked;
	my $i;
	my $array;

	# Set selected values
	for ($i=1;$i<=$#array;$i++) {
		$checked = 0;
		foreach (split(/:/,$cfg->{"DONGLE1"}->{protocols} ))  {
			if ($_ eq $array[$i]->{value}) {
				$checked = 1;
			}
		}
		# list all Sensors from array
		$sensors .= $cgi->checkbox(
			-name    => "sensors$array[$i]->{value}",
			-id      => "sensors$array[$i]->{value}",
			-class   => "toggle",
			-checked => $checked,
			-value   => $array[$i]->{value},
			-label   => $array[$i]->{protocol}." ".$array[$i]->{description},
		  );
	}
	$template->param( SENSORS => $sensors );
	
	#$content = $element;
	#print_test($content);
	printtemplate();
	exit;
}

#####################################################
# Save-Sub
#####################################################

sub save 
{
	#$cfg->{"DONGLE"}->{count} = $R::countdongles;
	
	$cfg->{"DONGLE1"}->{Serial} = $R::d1id1;
	$cfg->{"DONGLE1"}->{freq1} = $R::d1freq1;
	$cfg->{"DONGLE1"}->{freq2} = $R::d1freq2;
	$cfg->{"DONGLE1"}->{freq3} = $R::d1freq3;
	$cfg->{"DONGLE1"}->{freq4} = $R::d1freq4;
	$cfg->{"DONGLE1"}->{sample} = $R::d1sample;
	$cfg->{"DONGLE1"}->{hop} = $R::d1hop;
	if ($R::countdongles eq "1")  {	
		delete $cfg->{"DONGLE2"};
		delete $cfg->{"DONGLE3"};
	}
	
	# save all selected sensors/protocols
	our $sensors;
	for (my $i=1;$i<=$#array;$i++) {
 		if ( ${"R::sensors$array[$i]->{value}"} )   {
		#if ( ${param("sensors$array[$i])->{value}"} )   {
			if ( !$sensors ) {
				$sensors = "$array[$i]->{value}";
			} else {
				$sensors = "$sensors".":"."$array[$i]->{value}";
			}
		}
	}
	$cfg->{"DONGLE1"}->{protocols} = $sensors;
	
	if ($R::countdongles eq "2")  {
		$cfg->{"DONGLE2"}->{Serial} = $R::d2id1;
		$cfg->{"DONGLE2"}->{freq1} = $R::d2freq1;
		$cfg->{"DONGLE2"}->{freq2} = $R::d2freq2;
		$cfg->{"DONGLE2"}->{freq3} = $R::d2freq3;
		$cfg->{"DONGLE2"}->{freq4} = $R::d2freq4;
		$cfg->{"DONGLE2"}->{sample} = $R::d2sample;
		$cfg->{"DONGLE2"}->{hop} = $R::d2hop;
		
		delete $cfg->{"DONGLE3"};
	}
	if ($R::countdongles eq "3")  {
		$cfg->{"DONGLE2"}->{Serial} = $R::d2id1;
		$cfg->{"DONGLE2"}->{freq1} = $R::d2freq1;
		$cfg->{"DONGLE2"}->{freq2} = $R::d2freq2;
		$cfg->{"DONGLE2"}->{freq3} = $R::d2freq3;
		$cfg->{"DONGLE2"}->{freq4} = $R::d2freq4;
		$cfg->{"DONGLE2"}->{sample} = $R::d2sample;
		$cfg->{"DONGLE2"}->{hop} = $R::d2hop;
		
		$cfg->{"DONGLE3"}->{Serial} = $R::d3id1;
		$cfg->{"DONGLE3"}->{freq1} = $R::d3freq1;
		$cfg->{"DONGLE3"}->{freq2} = $R::d3freq2;
		$cfg->{"DONGLE3"}->{freq3} = $R::d3freq3;
		$cfg->{"DONGLE3"}->{freq4} = $R::d3freq4;
		$cfg->{"DONGLE3"}->{sample} = $R::d3sample;
		$cfg->{"DONGLE3"}->{hop} = $R::d3hop;
	}
	
	$jsonobj->write();
	# Call saving to rtl_433
	&rtl_433_form;
		
	&print_save;
	exit;
}
  


##########################################################################
# Init Template
##########################################################################

sub inittemplate
{
	$template = HTML::Template->new(
				filename => $lbptemplatedir . "/" . $templatefile,
				global_vars => 1,
				loop_context_vars => 1,
				die_on_bad_params=> 0,
				associate => $jsonobj,
				%htmltemplate_options,
				debug => 1,
				);
	# getting language file loaded
	our %L = LoxBerry::System::readlanguage($template, 'language.ini');
}

######################################################################
# AJAX functions
######################################################################

sub pids 
{
	$pids{'rscanner'} = trim(`pgrep rtl_433`);
	#LOGDEB "PIDs updated";
}	

sub ajax_header
{
	print $cgi->header(
			-type => 'application/json',
			-charset => 'utf-8',
			-status => '200 OK',
	);	
	#LOGOK "AJAX posting received and processed";
}

sub ajax_header_text
{
	print $cgi->header(
			-type => 'text/plain',
			-charset => 'utf-8',
			-status => '200 OK',
	);	
	#LOGOK "AJAX posting received and processed";

}

########################################################################
#rtl_433 Config Form 
########################################################################
sub rtl_433_form
{

	# Stop Service
	system("sudo systemctl stop rtl_433-mqtt.service");
	# Create rtl_433.conf file
	my $file = qx(/usr/bin/php $lbpbindir/create_conf.php);
	# Start Service using newly created file
	system("sudo systemctl start rtl_433-mqtt.service");
	return;

}

########################################################################
# change Serial Form 
########################################################################
sub change_serial
{
	my $No;
	
	# Stop Service
	system("sudo systemctl stop rtl_433-mqtt.service");
	sleep (1);
	system("yes 2>/dev/null | rtl_eeprom -d".$No." -s00000".$SerialNo." > /dev/null 2>&1");
	$cfg->{"DONGLE1"}->{Serial} = "00000".$SerialNo;
	$jsonobj->write();
	#my $file = qx(/usr/bin/php $lbpbindir/create_conf.php);
	system("sudo systemctl start rtl_433-mqtt.service");
	notify( $lbpplugindir, "Radioscanner", "Please restart LoxBerry or unplug/plugin the Dongle in order to apply the changed Serial No.");
	printtemplate();
	return;

}

##########################################################################
# Print Template
##########################################################################

sub printtemplate
{	
	LoxBerry::Web::lbheader("$plugin->{PLUGINDB_TITLE} v$version", "https://wiki.loxberry.de/plugins/radioscanner/start", "");
	print LoxBerry::Log::get_notifications_html($lbpplugindir);
	print $template->output();
	LoxBerry::Web::lbfooter();
	exit;
}

##########################################################################
# Print for testing
##########################################################################

sub print_test($content)
{
	# Print Template
	print "Content-Type: text/html; charset=utf-8\n\n"; 
	print "*********************************************************************************************";
	print "<br>";
	print " *** Ausgabe zu Testzwecken";
	print "<br>";
	print "*********************************************************************************************";
	print "<br>";
	print "<br>";
	print Dumper($content); 
	exit;
}

#####################################################
# Save
#####################################################

sub print_save
{
	$template->param("SAVE", "1");
	my $template_title = "$L{'BASIS.MAIN_TITLE'}: v$version";
	LoxBerry::Web::lbheader($template_title, $helplink, $helptemplate);
	print $template->output();
	LoxBerry::Web::lbfooter();
	exit;
}

#####################################################
# Error-Sub
#####################################################

sub error 
{
	$template->param("ERROR", "1");
	my $template_title = $L{'ERRORS.MY_NAME'} . ": v$version - " . $L{'ERRORS.ERR_TITLE'};
	LoxBerry::Web::lbheader($template_title, $helplink, $helptemplate);
	$template->param('ERR_MESSAGE', $error_message);
	print $template->output();
	LoxBerry::Web::lbfooter();
	exit;
}

##########################################################################
# END routine - is called on every exit (also on exceptions)
##########################################################################
sub END 
{	
	our @reason;
	
	if ($log) {
		if (@reason) {
			LOGCRIT "Unhandled exception catched:";
			LOGERR @reason;
			LOGEND "Finished with an exception";
		} elsif ($error_message) {
			LOGEND "Finished with error: ".$error_message;
		} else {
			#LOGEND "Finished successful";
		}
	}
}


