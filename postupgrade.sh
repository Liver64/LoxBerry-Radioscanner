#!/bin/bash

# Restore the plugin configuration preserved by preupgrade.sh.
# Exit codes: 0 = success, 1 = warning, 2 = cancel installation.

ARGV0=$0
ARGV1=$1
ARGV2=$2
ARGV3=$3
ARGV4=$4
ARGV5=$5

BASEFOLDER=${LBHOMEDIR:-$ARGV5}
BACKUPROOT="/tmp/${ARGV1}_upgrade"
BACKUPDIR="$BACKUPROOT/config/${ARGV3}"
TARGETDIR="$BASEFOLDER/config/plugins/$ARGV3"

if [ -d "$BACKUPDIR" ]; then
    echo "<INFO> Copy back existing config files"
    mkdir -p "$TARGETDIR" || {
        echo "<ERROR> Could not create plugin configuration directory."
        exit 2
    }
    cp -a "$BACKUPDIR/." "$TARGETDIR/" || {
        echo "<ERROR> Restoring existing plugin configuration failed."
        exit 2
    }
else
    echo "<WARNING> No upgrade configuration backup found; nothing to restore."
fi

rm -rf "$BACKUPROOT"
exit 0
