#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
validation=/opt/validation/twrp-RMX3125-20261022-2246
test ! -e "$validation/ramdisk.cpio"
gzip -dc "$validation/ramdisk" > "$validation/ramdisk.cpio"
cpio --list --verbose --numeric-uid-gid --quiet < "$validation/ramdisk.cpio" > "$validation/ramdisk-contents.txt"
head -n 14 "$validation/ramdisk-contents.txt"
grep -E ' (prop.default|default.prop|init|system/bin/recovery|system/lib64/libtwrpfscrypt.so|vendor/lib64/hw/gatekeeper.oppo6833.so)( |$)' "$validation/ramdisk-contents.txt"
