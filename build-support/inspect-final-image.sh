#!/usr/bin/env bash
set -euo pipefail
export PATH=/opt/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
cd /opt/twrp
image=out/target/product/RMX3125/recovery.img
validation=/opt/validation/twrp-RMX3125-20261022-2246
test -s "$image"
test ! -e "$validation"
mkdir -p /opt/validation
mkdir "$validation"
python3 system/tools/mkbootimg/unpack_bootimg.py --boot_img "$image" --out "$validation" > "$validation/header.txt"
out/host/linux-x86/bin/avbtool info_image --image "$image" > "$validation/avb-info.txt"
out/host/linux-x86/bin/avbtool verify_image --image "$image" --key external/avb/test/data/testkey_rsa2048.pem > "$validation/avb-verify.txt"
cat "$validation/header.txt"
cat "$validation/avb-verify.txt"
od -An -tx1 -N4 "$validation/ramdisk"
