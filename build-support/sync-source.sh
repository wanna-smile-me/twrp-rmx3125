#!/usr/bin/env bash
set -euo pipefail
export PATH=/opt/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export GIT_TERMINAL_PROMPT=0
cd /opt/twrp
git config --global user.name 'Local TWRP build'
git config --global user.email build@localhost
git config --global http.lowSpeedLimit 1
git config --global http.lowSpeedTime 120
git config --global http.version HTTP/1.1
git config --global http.https://github.com/.proxy http://127.0.0.1:17890
# The verified Windows proxy now reaches the original AOSP host as well.
git config --global --unset-all url.https://mirrors.ustc.edu.cn/aosp/.insteadOf || test "$?" = 5
git config --global http.https://android.googlesource.com/.proxy http://127.0.0.1:17890
if [[ ! -e .repo/manifest.xml ]]; then
    timeout 600 repo init --repo-url=https://github.com/GerritCodeReview/git-repo.git --depth=1 --no-clone-bundle -u https://github.com/TWRP-Test/platform_manifest_twrp_aosp.git -b twrp-16.0 > /opt/logs/repo-init.log 2>&1
fi
repo manifest -o /opt/logs/manifest-initial.xml
# Leave headroom for VHD metadata and downloads below the approved 80 GB cap.
limit=$((68 * 1024 * 1024 * 1024))
used=$(df -B1 --output=used / | tail -1 | tr -d ' ')
test "$used" -lt "$limit"
setsid repo sync -c --no-tags --no-clone-bundle --fail-fast -j2 > /opt/logs/repo-sync.log 2>&1 &
sync_pid=$!
while kill -0 "$sync_pid" 2>/dev/null; do
    used=$(df -B1 --output=used / | tail -1 | tr -d ' ')
    if ((used >= limit)); then
        printf 'SPACE_LIMIT_REACHED: %s bytes\n' "$used" | tee /opt/logs/space-limit.txt
        kill -TERM -- "-$sync_pid"
        wait "$sync_pid" || true
        exit 75
    fi
    sleep 2
done
wait "$sync_pid"
repo manifest -r -o /opt/logs/manifest-pinned.xml
printf 'SOURCE_SYNC_COMPLETE\n'
