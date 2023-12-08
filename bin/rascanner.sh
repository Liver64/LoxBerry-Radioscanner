#!/bin/bash

plugindir=REPLACELBPPLUGINDIR

exit_script() {
	echo -e "\nStopping scanner and restarting MQTT Service...\n"
	trap - SIGINT SIGTERM # clear the trap
	sudo systemctl start rtl_433-mqtt.service > /dev/null 2>&1 
	systemctl --no-pager status rtl_433-mqtt.service
	kill -- -$$ # Sends SIGTERM to child/sub processes
}

trap exit_script SIGINT SIGTERM

if systemctl --no-pager status rtl_433-mqtt.service > /dev/null 2>&1; then
	echo -e "\nStopping MQTT Service and starting scanner...\n"
	sudo systemctl stop rtl_433-mqtt.service > /dev/null 2>&1
fi

# Commandline options
if [[ -z "$@" ]]; then
	echo "No commandline options: using config $LBPCONFIG/$plugindir/config.json"
	for i in {1..5}; do
		if [[ `jq -r ".DONGLE$i" $LBPCONFIG/$plugindir/config.json` == "null" ]]; then
			break
		else
			freq1=`jq -r ".DONGLE$i.freq1" $LBPCONFIG/$plugindir/config.json`
			freq2=`jq -r ".DONGLE$i.freq2" $LBPCONFIG/$plugindir/config.json`
			freq3=`jq -r ".DONGLE$i.freq3" $LBPCONFIG/$plugindir/config.json`
			freq4=`jq -r ".DONGLE$i.freq4" $LBPCONFIG/$plugindir/config.json`
			hop=`jq -r ".DONGLE$i.hop" $LBPCONFIG/$plugindir/config.json`
			sample=`jq -r ".DONGLE$i.sample" $LBPCONFIG/$plugindir/config.json`
			for z in {1..4}; do
				varname="freq$z"
				if [[ ! -z ${!varname} ]] && [[ ${!varname} != "0" ]]; then
					CMD="$CMD -f ${!varname}"
				fi
			done
			if [[ ! -z $hop ]];then
				CMD="$CMD -H ${hop}"
			fi
			if [[ ! -s $sample ]];then
				CMD="$CMD -s ${sample}"
			fi
		fi
	done
	echo -e "rtl_433 options: $CMD -F kv -M time -M protocol -M level -M noise\n"
else
	echo "Using commandline options: $@"
	echo -e "rtl_433 options: $@ -F kv -M time -M protocol -M level -M noise\n"
	CMD=$@
fi

rtl_433 ${CMD} -F kv -M time -M protocol -M level -M noise 
