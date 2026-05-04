#!/bin/bash
# Dump a CH-8 doll's USB disk image
# Usage: ./tools/dump_doll.sh

VOLUME=$(ls /Volumes/ | grep -v "Macintosh HD" | grep -v "com.apple" | grep -v "Kiro" | head -1)

if [ -z "$VOLUME" ]; then
    echo "No CH-8 volume found. Plug in a doll via USB-C."
    exit 1
fi

echo "Found volume: $VOLUME"
cat "/Volumes/$VOLUME/version.txt"
echo ""

# Get the disk device
DISK=$(diskutil list | grep "$VOLUME" | awk '{print $NF}' | sed 's/s[0-9]*$//')
echo "Disk device: $DISK"

NAME=$(echo "$VOLUME" | tr '[:upper:]' '[:lower:]')
OUTFILE="dumps/${NAME}_usb_disk.img"

mkdir -p dumps

echo "Dumping to $OUTFILE..."
sudo dd if=/dev/r${DISK} of="$OUTFILE" bs=512 2>&1
echo "Done: $(wc -c < "$OUTFILE") bytes"
