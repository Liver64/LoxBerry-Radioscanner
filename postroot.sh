#!/bin/bash

# Bashscript which is executed by bash *AFTER* complete installation is done
# (*AFTER* postinstall but *BEFORE* postupdate). Use with caution and remember,
# that all systems may be different!
#
# Exit code must be 0 if executed successfull. 
# Exit code 1 gives a warning but continues installation.
# Exit code 2 cancels installation.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Will be executed as user "root".
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# You can use all vars from /etc/environment in this script.
#
# We add 5 additional arguments when executing this script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"

# To use important variables from command line use the following code:
COMMAND=$0    # Zero argument is shell command
PTEMPDIR=$1   # First argument is temp folder during install
PSHNAME=$2    # Second argument is Plugin-Name for scipts etc.
PDIR=$3       # Third argument is Plugin installation folder
PVERSION=$4   # Forth argument is Plugin version
#LBHOMEDIR=$5 # Comes from /etc/environment now. Fifth argument is
              # Base folder of LoxBerry

# Combine them with /etc/environment
PCGI=$LBPCGI/$PDIR
PHTML=$LBPHTML/$PDIR
PTEMPL=$LBPTEMPL/$PDIR
PDATA=$LBPDATA/$PDIR
PLOG=$LBPLOG/$PDIR # Note! This is stored on a Ramdisk now!
PCONFIG=$LBPCONFIG/$PDIR
PSBIN=$LBPSBIN/$PDIR
PBIN=$LBPBIN/$PDIR

echo "<INFO> Start building rtl-sdr"
cd ~
cd /usr/local
mkdir rtl
cd /usr/local/rtl
git clone git://git.osmocom.org/rtl-sdr.git
cd /usr/local/rtl/rtl-sdr/ && mkdir build && cd build/
cmake ../ -DINSTALL_UDEV_RULES=ON
sudo make
sudo make install
sudo cp REPLACELBPBINDIR/rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig

cp REPLACELBPCONFIGDIR/examples/no-rtl.conf /etc/modprobe.d/no-rtl.conf
echo "<OK> Blacklist file has been copied to /etc/modprobe.d/no-rtl.conf"

echo "<INFO> Start building rtl_433"
cd ~
cd /usr/local/rtl
git clone https://github.com/merbanan/rtl_433.git
cd /usr/local/rtl/rtl_433/ && mkdir build/
cd build && cmake ../
make
sudo make install

cp REPLACELBPCONFIGDIR/examples/rtl_433-mqtt.service /etc/systemd/system/rtl_433-mqtt.service
echo "<OK> Service file 'rtl_433-mqtt.service' has been copied to /etc/systemd/system/"

echo "<INFO> rtl_433 will be configured to start as Service"
sudo systemctl enable rtl_433-mqtt
sudo systemctl start rtl_433-mqtt

# Exit with Status 0
exit 0
