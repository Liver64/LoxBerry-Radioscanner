#!/bin/bash


#RTL-SDR Dongles anzeigen WebUI
lsusb >/tmp/dvb-dongle_full.txt
sed -n '/RTL28/p' /tmp/dvb-dongle_full.txt >/tmp/dvb-dongle.txt
rm /tmp/dvb-dongle_full.txt
