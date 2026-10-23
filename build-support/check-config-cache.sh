#!/usr/bin/env bash
set -eo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(cd -- "$script_dir/.." && pwd -P)
export PATH=/opt/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C.UTF-8 BUILD_USERNAME=local BUILD_HOSTNAME=rmx3125-build GOMAXPROCS=4
export ALLOW_MISSING_DEPENDENCIES=true SOONG_GOMEMLIMIT=10GiB
cd /opt/twrp
source build/envsetup.sh
lunch twrp_RMX3125-bp2a-eng > /opt/logs/cache-check-lunch.log 2>&1
: > /opt/logs/config-cache-check.log
configure() {
    TARGET_BUILD_VARIANT="$1" build/soong/soong_ui.bash --make-mode --config-only --skip-ninja recoveryimage >> /opt/logs/config-cache-check.log 2>&1
    python3 - "$2" <<'PY'
import hashlib, json, pathlib, sys
p = pathlib.Path('out/soong/soong.twrp_RMX3125.variables')
snapshot = {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'mtime_ns': p.stat().st_mtime_ns}
pathlib.Path('/opt/logs/config-cache-' + sys.argv[1] + '.json').write_text(json.dumps(snapshot))
PY
}
configure eng first
configure eng second
configure userdebug changed
configure eng restored
python3 - <<'PY'
import json, pathlib
snapshots = {name: json.loads(pathlib.Path('/opt/logs/config-cache-' + name + '.json').read_text()) for name in ('first', 'second', 'changed', 'restored')}
a, b, c, d = (snapshots[n] for n in ('first', 'second', 'changed', 'restored'))
assert a == b, 'Identical configuration changed contents or timestamp'
assert c['sha256'] != b['sha256'] and c['mtime_ns'] != b['mtime_ns'], 'Changed configuration was not written'
assert d['sha256'] == a['sha256'], 'eng configuration was not restored exactly'
print('PASS: identical config keeps hash/mtime; changed config updates; eng restored exactly.')
pathlib.Path('/opt/logs/config-cache-test.json').write_text(json.dumps(snapshots, indent=2))
PY
git -C build/make diff --check
git -C build/make diff -- core/soong_config.mk > "$project_root/evidence/soong-config-cache.patch"
