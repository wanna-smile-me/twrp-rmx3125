#!/usr/bin/env bash
set -euo pipefail
swap=/opt/twrp-build.swap
test ! -L "$swap"
bytes=6442450944
if [[ -e "$swap" ]]; then
    test -f "$swap"
    test "$(stat -c %a "$swap")" = 600
    test "$(blkid -p -s TYPE -o value "$swap")" = swap
    size=$(stat -c %s "$swap")
    test "$size" = 2147483648 -o "$size" = "$bytes"
    if [[ "$size" != "$bytes" ]]; then
        if grep -q "^$swap " /proc/swaps; then swapoff "$swap"; fi
        fallocate -l "$bytes" "$swap"
        mkswap "$swap"
    fi
fi
if [[ ! -e "$swap" ]]; then
    umask 077
    fallocate -l "$bytes" "$swap"
    chmod 600 "$swap"
    mkswap "$swap"
fi
test -f "$swap"
test "$(stat -c %s "$swap")" = "$bytes"
test "$(stat -c %a "$swap")" = 600
test "$(blkid -p -s TYPE -o value "$swap")" = swap
if ! grep -q "^$swap " /proc/swaps; then
    swapon "$swap"
fi
grep -q "^$swap " /proc/swaps
free -h
