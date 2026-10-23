#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
cpio --extract --to-stdout --quiet --no-absolute-filenames -- prop.default < /opt/validation/twrp-RMX3125-20261022-2246/ramdisk.cpio | grep -E '^(ro.build.version.release|ro.build.version.security_patch|ro.vendor.build.security_patch|keymaster_ver|ro.crypto.type|ro.crypto.state|sys.boot_completed)='
