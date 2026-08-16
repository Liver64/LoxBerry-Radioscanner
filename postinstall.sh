#!/bin/bash

# Runs as user loxberry after plugin files have been copied.
# Exit codes: 0 = success, 1 = warning, 2 = cancel installation.

COMMAND=$0
PTEMPDIR=$1
PSHNAME=$2
PDIR=$3
PVERSION=$4

PCGI=$LBPCGI/$PDIR
PHTML=$LBPHTML/$PDIR
PTEMPL=$LBPTEMPL/$PDIR
PDATA=$LBPDATA/$PDIR
PLOG=$LBPLOG/$PDIR
PCONFIG=$LBPCONFIG/$PDIR
PSBIN=$LBPSBIN/$PDIR
PBIN=$LBPBIN/$PDIR

echo "<INFO> Start building usbreset"
cd "$PBIN" || {
    echo "<ERROR> Could not enter plugin bin directory: $PBIN"
    exit 2
}

if ! gcc usbreset.c -o usbreset; then
    echo "<ERROR> Building usbreset failed."
    exit 2
fi

chmod +x usbreset || {
    echo "<ERROR> Could not make usbreset executable."
    exit 2
}

echo "<OK> usbreset built successfully."
exit 0
