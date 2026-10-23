"""Copy this device's recovery HALs and their ELF dependencies; run inside the build WSL."""
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys

stock = Path('/opt/stock-ramdisk')
device = Path(sys.argv[1]).resolve()
root = device / 'recovery/root'
entries = {
    'system/bin/android.hardware.keymaster@4.0-service.trustonic': 'vendor/bin/hw/android.hardware.keymaster@4.0-service.trustonic',
    'vendor/bin/hw/android.hardware.gatekeeper@1.0-service': 'vendor/bin/hw/android.hardware.gatekeeper@1.0-service',
    'vendor/bin/mcDriverDaemon': 'vendor/bin/mcDriverDaemon',
    'system/bin/hw/vendor.oplus.hardware.cryptoeng@1.0-service': 'vendor/bin/hw/vendor.oplus.hardware.cryptoeng@1.0-service',
}
for module in (stock / 'vendor/lib64/hw').glob('*.so'):
    entries[str(module.relative_to(stock))] = str(module.relative_to(stock))

manifest = []
pending = []
copied = set()
core = {'libc.so', 'libm.so', 'libdl.so'}

def copy_elf(source, destination):
    source = source.resolve(strict=True)
    assert source.is_relative_to(stock), f'ELF outside stock recovery: {source}'
    data = source.read_bytes()
    assert data[:5] == b'\x7fELF\x02' and data[18:20] == b'\xb7\x00', f'Not ARM64 ELF: {source}'
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination.chmod(0o755 if '/bin/' in str(destination) else 0o644)
    assert hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(data).digest()
    output = subprocess.check_output(['readelf', '-d', str(source)], text=True)
    needed = re.findall(r'Shared library: \[(.+?)\]', output)
    assert all('/' not in name for name in needed), 'Unexpected library path'
    pending.extend(needed)
    manifest.append(f'{hashlib.sha256(data).hexdigest()}  {destination.relative_to(device)}  source={source.relative_to(stock)}')

for source, destination in entries.items():
    copy_elf(stock / source, root / destination)

while pending:
    name = pending.pop()
    if name in copied or name in core:
        continue
    candidates = [stock / 'vendor/lib64' / name, stock / 'system/lib64' / name]
    source = next((path for path in candidates if path.exists()), None)
    if source is None:
        raise FileNotFoundError(f'Stock HAL dependency missing: {name}')
    copied.add(name)
    copy_elf(source, root / 'vendor/lib64' / name)

for relative in ['vendor/app/mcRegistry', 'odm/vendor/app/mcRegistry']:
    assert (stock / relative).is_dir(), f'Trustonic registry missing: {relative}'
    shutil.copytree(stock / relative, root / relative, dirs_exist_ok=True)
for part, target in [('kernel', 'kernel'), ('dtb', 'dtb/mt6833.dtb'), ('recovery_dtbo', 'recovery_dtbo')]:
    source = device.parents[2] / 'stock/unpacked' / part
    assert source.is_file(), f'Missing original image component: {source}'
    destination = device / 'prebuilt' / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    assert hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest()

(device / 'stock-blob-sha256.txt').write_text('\n'.join(sorted(manifest)) + '\n')
print(f'Copied {len(entries)} HAL files and {len(copied)} shared libraries; hashes and ARM64 headers verified.')
