#!/bin/bash

# Bashscript which is executed by bash as the final installation step.
# It runs as root and is used here to build/install rtl-sdr + rtl_433 and
# configure the systemd integration.
#
# Exit codes used by the LoxBerry installer:
#   0 = success
#   1 = warning (installation continues)
#   2 = fatal error (installation is cancelled)

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

RTL_BASE=/usr/local/rtl
RTL_SDR_DIR=$RTL_BASE/rtl-sdr
RTL_433_DIR=$RTL_BASE/rtl_433
RTL_MANIFEST_DIR=$RTL_BASE/install-manifests
RTL_SDR_SAVED_MANIFEST=$RTL_MANIFEST_DIR/rtl-sdr.txt
RTL_433_SAVED_MANIFEST=$RTL_MANIFEST_DIR/rtl_433.txt

fatal()
{
    echo "<ERROR> $*"
    exit 2
}

mkdir -p "$RTL_BASE" "$RTL_MANIFEST_DIR" || fatal "Could not create $RTL_BASE."

# Preserve a cumulative list of every file installed by CMake. This keeps
# uninstall reliable across upgrades even if upstream later removes/renames
# an installed file. Existing manifests are merged before a source tree is
# replaced.
merge_install_manifest()
{
    source_manifest="$1"
    saved_manifest="$2"

    [ -s "$source_manifest" ] || return 0

    tmp_manifest=$(mktemp "$RTL_MANIFEST_DIR/.manifest.XXXXXX") || return 1
    if [ -s "$saved_manifest" ]; then
        cat "$saved_manifest" "$source_manifest" | sort -u > "$tmp_manifest" || {
            rm -f "$tmp_manifest"
            return 1
        }
    else
        sort -u "$source_manifest" > "$tmp_manifest" || {
            rm -f "$tmp_manifest"
            return 1
        }
    fi
    mv -f "$tmp_manifest" "$saved_manifest"
}

echo "<INFO> Start building rtl-sdr"
merge_install_manifest "$RTL_SDR_DIR/build/install_manifest.txt" "$RTL_SDR_SAVED_MANIFEST" \
    || fatal "Could not preserve previous rtl-sdr install manifest."

# Use a clean source tree. The already installed /usr/local binaries/libraries
# remain in place until make install succeeds, so an unsuccessful clone/build
# does not remove the previously installed runtime files.
rm -rf "$RTL_SDR_DIR"
git clone https://gitea.osmocom.org/sdr/rtl-sdr.git "$RTL_SDR_DIR" \
    || fatal "Could not clone rtl-sdr source repository."

mkdir -p "$RTL_SDR_DIR/build" || fatal "Could not create rtl-sdr build directory."
cd "$RTL_SDR_DIR/build" || fatal "Could not enter rtl-sdr build directory."
cmake ../ -DINSTALL_UDEV_RULES=ON || fatal "Configuring rtl-sdr failed."
make || fatal "Building rtl-sdr failed."
make install || fatal "Installing rtl-sdr failed."
merge_install_manifest "$RTL_SDR_DIR/build/install_manifest.txt" "$RTL_SDR_SAVED_MANIFEST" \
    || fatal "Could not save rtl-sdr install manifest."

cp "$PBIN/rtl-sdr.rules" /etc/udev/rules.d/rtl-sdr.rules \
    || fatal "Could not install rtl-sdr udev rules."
ldconfig || fatal "ldconfig failed after installing rtl-sdr."

cp "$PCONFIG/examples/no-rtl.conf" /etc/modprobe.d/no-rtl.conf \
    || fatal "Could not install DVB driver blacklist."
echo "<OK> Blacklist file has been copied to /etc/modprobe.d/no-rtl.conf"

echo "<INFO> Start building rtl_433"
merge_install_manifest "$RTL_433_DIR/build/install_manifest.txt" "$RTL_433_SAVED_MANIFEST" \
    || fatal "Could not preserve previous rtl_433 install manifest."
rm -rf "$RTL_433_DIR"
git clone https://github.com/merbanan/rtl_433.git "$RTL_433_DIR" \
    || fatal "Could not clone rtl_433 source repository."

mkdir -p "$RTL_433_DIR/build" || fatal "Could not create rtl_433 build directory."
cd "$RTL_433_DIR/build" || fatal "Could not enter rtl_433 build directory."
cmake ../ || fatal "Configuring rtl_433 failed."
make || fatal "Building rtl_433 failed."
make install || fatal "Installing rtl_433 failed."
merge_install_manifest "$RTL_433_DIR/build/install_manifest.txt" "$RTL_433_SAVED_MANIFEST" \
    || fatal "Could not save rtl_433 install manifest."
ldconfig || fatal "ldconfig failed after installing rtl_433."

cp "$PCONFIG/examples/rtl_433-mqtt.service" /etc/systemd/system/rtl_433-mqtt.service \
    || fatal "Could not install rtl_433-mqtt.service."
echo "<OK> Service file 'rtl_433-mqtt.service' has been copied to /etc/systemd/system/"

echo "<INFO> rtl_433 will be configured to start as Service"
systemctl daemon-reload || fatal "systemd daemon-reload failed."
systemctl enable rtl_433-mqtt.service || fatal "Could not enable rtl_433-mqtt.service."

# On a fresh installation the user has not saved RadioScanner settings yet,
# so rtl_433.conf does not exist. Enable the service now, but only start it
# immediately when a configuration already exists (typically on upgrades).
if [ -s "$PCONFIG/rtl_433.conf" ]; then
    systemctl restart rtl_433-mqtt.service || fatal "Could not start rtl_433-mqtt.service."
    sleep 2
    systemctl is-active --quiet rtl_433-mqtt.service \
        || fatal "rtl_433-mqtt.service did not become active."
else
    systemctl stop rtl_433-mqtt.service 2>/dev/null || true
    echo "<INFO> No rtl_433.conf yet. Service is enabled and will start after settings are saved."
fi

echo "<INFO> Creating symlink for rascanner"
chmod +x "$PBIN/rascanner.sh" || fatal "Could not make rascanner executable."
rm -f /usr/local/bin/rascanner
ln -s "$PBIN/rascanner.sh" /usr/local/bin/rascanner \
    || fatal "Could not create /usr/local/bin/rascanner."

if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules 2>/dev/null || true
fi

echo "<OK> RadioScanner system components installed successfully."
exit 0
