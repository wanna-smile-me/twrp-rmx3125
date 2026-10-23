#!/usr/bin/env bash
set -eo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(cd -- "$script_dir/.." && pwd -P)
export PATH=/opt/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C.UTF-8
export BUILD_USERNAME=local
export BUILD_HOSTNAME=rmx3125-build
export GOMEMLIMIT=5GiB
export SOONG_GOMEMLIMIT=10GiB
export GOMAXPROCS=4
export ALLOW_MISSING_DEPENDENCIES=true
stage=${1:-all}
case "$stage" in
    all|compile) ;;
    *) printf 'Usage: %s [all|compile]\n' "$0" >&2; exit 64 ;;
esac
if [[ "$stage" == all ]]; then
    bash "$script_dir/setup-build-memory.sh"
fi
cd /opt/twrp
test -s /opt/logs/manifest-pinned.xml
python3 "$project_root/verify_device_tree.py"
rsync -a "$project_root/device/realme/RMX3125/" device/realme/RMX3125/
test -s device/realme/RMX3125/prebuilt/kernel
source build/envsetup.sh
lunch twrp_RMX3125-bp2a-eng > /opt/logs/lunch.log 2>&1
test "$(get_build_var TARGET_DEVICE)" = RMX3125
test "$(get_build_var BOARD_BOOT_HEADER_VERSION)" = 2
test "$(get_build_var BOARD_RECOVERYIMAGE_PARTITION_SIZE)" = 134217728
limit=$((80 * 1024 * 1024 * 1024))
# Reserve 500 MB for host files and guard latency within the approved 90 GB total.
vhd_limit=89500000000
vhd=/mnt/d/Build/TWRP-RMX3125/wsl/ext4.vhdx
used=$(df -B1 --output=used / | tail -1 | tr -d ' ')
test "$used" -lt "$limit"
test "$(stat -c %s "$vhd")" -lt "$vhd_limit"
run_phase() {
    local build_jobs=$1
    shift
    setsid taskset -c 0-3 build/soong/soong_ui.bash --make-mode -j"$build_jobs" "$@" >> /opt/logs/build-recovery.log 2>&1 &
    local build_pid=$!
    while kill -0 "$build_pid" 2>/dev/null; do
        used=$(df -B1 --output=used / | tail -1 | tr -d ' ')
        vhd_size=$(stat -c %s "$vhd")
        if ((used >= limit || vhd_size >= vhd_limit)); then
            printf 'SPACE_LIMIT_REACHED: root=%s VHD=%s bytes\n' "$used" "$vhd_size" | tee /opt/logs/build-space-limit.txt
            kill -TERM -- "-$build_pid"
            wait "$build_pid" || true
            return 75
        fi
        sleep 0.1
    done
    wait "$build_pid"
}
if [[ "$stage" == all ]]; then
    printf 'BUILD_RULE_GENERATION\n' > /opt/logs/build-recovery.log
    run_phase 2 --skip-ninja recoveryimage
    bash "$script_dir/finish-build-memory.sh"
fi
printf 'RECOVERY_COMPILATION\n' >> /opt/logs/build-recovery.log
run_phase 4 recoveryimage
test -s out/target/product/RMX3125/recovery.img
sha256sum out/target/product/RMX3125/recovery.img | tee /opt/logs/recovery-sha256.txt
printf 'BUILD_COMPLETE_STATIC_VALIDATION_PENDING\n'
