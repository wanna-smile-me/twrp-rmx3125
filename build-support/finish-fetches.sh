#!/usr/bin/env bash
set -euo pipefail
limit=$((68 * 1024 * 1024 * 1024))
# Repo exited on another project's failure; preserve its two active large downloads.
group=3304
while kill -0 -- "-$group" 2>/dev/null; do
    used=$(df -B1 --output=used / | tail -1 | tr -d ' ')
    if ((used >= limit)); then
        printf 'SPACE_LIMIT_REACHED: %s bytes\n' "$used" | tee /opt/logs/space-limit.txt
        kill -TERM -- "-$group"
        exit 75
    fi
    sleep 2
done
bash /mnt/d/Build/TWRP-RMX3125/sync-source.sh
bash /mnt/d/Build/TWRP-RMX3125/build-recovery.sh
