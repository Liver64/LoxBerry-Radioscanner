#!/bin/bash

# Preserve the existing plugin configuration during an upgrade.
# Exit codes: 0 = success, 1 = warning, 2 = cancel installation.

ARGV0=$0
ARGV1=$1
ARGV2=$2
ARGV3=$3
ARGV4=$4
ARGV5=$5

BASEFOLDER=${LBHOMEDIR:-$ARGV5}
BACKUPDIR="/tmp/${ARGV1}_upgrade/config/${ARGV3}"
SOURCEDIR="$BASEFOLDER/config/plugins/$ARGV3"

echo "<INFO> Creating temporary folders for upgrading"
mkdir -p "$BACKUPDIR" || {
    echo "<ERROR> Could not create upgrade backup directory."
    exit 2
}

if [ -d "$SOURCEDIR" ]; then
    echo "<INFO> Backing up existing config files"
    cp -a "$SOURCEDIR/." "$BACKUPDIR/" || {
        echo "<ERROR> Backing up existing plugin configuration failed."
        exit 2
    }
else
    echo "<WARNING> No existing plugin configuration directory found; nothing to back up."
fi

exit 0
