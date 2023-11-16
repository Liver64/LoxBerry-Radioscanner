#!/bin/bash


# get RTL-SDR Dongles...
lsusb >/tmp/dvb-dongle_full.txt
sed -n '/RTL28/p' /tmp/dvb-dongle_full.txt >/tmp/dvb-dongle.txt
# ...an add Serial Number
lsusb -d 0bda:2838 -v | grep Serial >/tmp/dvb-dongle_ser.txt
sed -e 's/.*\(00000[0-9]*\).*/\1/' /tmp/dvb-dongle_ser.txt >/tmp/dvb-dongle_serial.txt
rm /tmp/dvb-dongle_full.txt
rm /tmp/dvb-dongle_ser.txt
