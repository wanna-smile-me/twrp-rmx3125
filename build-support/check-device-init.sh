#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(cd -- "$script_dir/.." && pwd -P)
shopt -s failglob
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
cd /opt/twrp
verifier=out/host/linux-x86/bin/host_init_verifier
test -x "$verifier"
args=()
for part in system system_ext vendor odm product; do
    passwd=out/target/product/RMX3125/obj/ETC/passwd_${part}_intermediates/passwd_${part}
    context_part=$part
    if [[ $part == system ]]; then context_part=plat; fi
    contexts=out/target/product/RMX3125/obj/ETC/${context_part}_property_contexts_intermediates/${context_part}_property_contexts
    test -f "$passwd"
    test -f "$contexts"
    args+=(-p "$passwd" "--property-contexts=$contexts")
done
for script in "$project_root"/device/realme/RMX3125/recovery/root/init.recovery*.rc; do
    "$verifier" "${args[@]}" "$script"
    printf 'PASS: %s\n' "${script##*/}"
done
