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

use CGI::Carp qw(fatalsToBrowser);
use CGI qw/:standard/;
use CGI;
use LWP::UserAgent;
use File::HomeDir;
use Cwd 'abs_path';
use JSON qw( decode_json );
use utf8;
use warnings;
use strict;
use Data::Dumper;

##########################################################################
# Generic exception handler
##########################################################################

# Every non-handled exceptions sets the @reason variable that can
# be written to the logfile in the END function

$SIG{__DIE__} = sub { our @reason = @_ };

##########################################################################
# Variables
##########################################################################

our $template;
our $navbar;
our $lbptemplatedir;
our $content;
our %navbar;
our $templatefile = "index.html";
our $tmp_log_file = "/tmp/scan4lox_log.tmp";
my $languagefile  = "rscan.ini";
my $pluginconfigfile = "config.cfg";
my $pluginlogfile = "rscan4lox.log";
my $helptemplate = "help.html";
my $helplink = "to be created";
my $error_message = "";
our $log = LoxBerry::Log->new ( name => 'Radioscanner UI', filename => $lbplogdir ."/". $pluginlogfile, append => 1, addtime => 1 );
our $pcfg = new Config::Simple($lbpconfigdir . "/" . $pluginconfigfile);
#my %Config = $pcfg->vars() if ( $pcfg );
our $plugin = LoxBerry::System::plugindata();

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
## Handle all ajax requests 
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



#my $saveformdata = defined $R::saveformdata ? $R::saveformdata : undef;
#my $do = defined $R::do ? $R::do : "form";

# Wir holen uns die Plugin-Config in den Hash %pcfg. Damit kannst du die Parameter mit $pcfg{'Section.Label'} direkt auslesen.
#my %pcfg;
#tie %pcfg, "Config::Simple", "$lbpconfigdir/$pluginconfigfile";
 

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
}

LOGSTART "Radioscanner UI started";


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
		#LOGERR "old Log: " . $oldlog;
		#LOGERR "act Log: " . $act_level;
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


$navbar{1}{Name} = "$L{'BASIS.MENU_SETTINGS'}";
$navbar{1}{URL} = './index.cgi';
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
} elsif ($R::do eq "logfiles") {
	LOGTITLE "Show logfiles";
	$navbar{99}{active} = 1;
	$template->param("LOGFILES", "1");
	$template->param("LOGLIST_HTML", LoxBerry::Web::loglist_html());
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
	# detect SDR Dongles
	our $count;
	system($lbpbindir . '/service.sh');
	my $filename = '/tmp/dvb-dongle.txt';
	open my $in, $filename;
	my $dongle_list;
	my $counter;
	while (my $line = <$in>) {
			$counter++;
            $dongle_list.= $counter -1 .": ". $line.'<br>';
        }
	$count = `wc -l < $filename`;
	if ($count < 1)  {
		$dongle_list = "****** No RTL-SDR compatible DVB-T Dongles detected ******";
	} else {
		$template->param("COUNT_DONGLE", $count);
	}
    $template->param("SC_LIST", $dongle_list);
	close($in);
	
	printtemplate();
	exit;
}

#####################################################
# Save-Sub
#####################################################

sub save 
{
	$pcfg->param("DONGLE1.ID", "$R::d1id1");
	$pcfg->param("DONGLE1.freq1", "$R::d1freq1");
	$pcfg->param("DONGLE1.freq2", "$R::d1freq2");
	$pcfg->param("DONGLE1.freq3", "$R::d1freq3");
	$pcfg->param("DONGLE1.freq4", "$R::d1freq4");
	$pcfg->param("DONGLE1.sample", "$R::d1sample");
	$pcfg->param("DONGLE1.hop", "$R::d1hop");
	#$pcfg->param("VARIOUS.donate", "$R::donate");
	
	$pcfg->save() or &error;
	
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
				associate => $pcfg,
				%htmltemplate_options,
				debug => 1,
				);
	# getting language file loaded
	our %L = LoxBerry::System::readlanguage($template, $languagefile);
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

########################################################################
#rtl_433 Config Form 
########################################################################
sub rtl_433_form
{

	# Stop Service
	system("sudo systemctl stop rtl_433-mqtt.service");
	# Create rtl_433.conf file
	my $file = qx(/usr/bin/php $lbphtmldir/create_conf.php);
	# Start Service using newly created file
	system("sudo systemctl start rtl_433-mqtt.service");
	return;

}

##########################################################################
# Print Template
##########################################################################

sub printtemplate
{	
	LoxBerry::Web::lbheader("$plugin->{PLUGINDB_TITLE} v$version", $helplink, $helptemplate);
	print LoxBerry::Log::get_notifications_html($lbpplugindir);
	print $template->output();
	LoxBerry::Web::lbfooter();
	exit;
}

##########################################################################
# Print for testing
##########################################################################

sub print_test
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
	print $content; 
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


