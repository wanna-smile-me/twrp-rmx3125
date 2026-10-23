#!/usr/bin/env bash
set -euo pipefail
swap=/opt/twrp-build.swap
test ! -L "$swap"
test "$(readlink -f "$swap")" = /opt/twrp-build.swap
test -f "$swap"
test "$(stat -c %s "$swap")" = 6442450944
test "$(stat -c %a "$swap")" = 600
test "$(blkid -p -s TYPE -o value "$swap")" = swap
if grep -q "^$swap " /proc/swaps; then swapoff "$swap"; fi
# User approved deleting only this build's temporary swap after rule generation.
rm -- "$swap"
test ! -e "$swap"
/usr/sbin/fstrim --verbose /
free -h
