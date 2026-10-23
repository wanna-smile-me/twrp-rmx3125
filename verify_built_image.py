"""Check the actual packaged RMX3125 image without extracting its filesystem."""
import gzip
import hashlib
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import struct
import sys
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parent
device = base / 'device/realme/RMX3125'
image = Path(sys.argv[1])
data = image.read_bytes()
assert len(data) == 134217728 and data[:8] == b'ANDROID!'
kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page, version = struct.unpack_from('<9I', data, 8)
assert (kernel_addr, ramdisk_addr, second_size, second_addr, tags_addr, page, version) == (0x40080000, 0x51100000, 0, 0, 0x47c80000, 2048, 2)
dtbo_size, dtbo_offset, header_size = struct.unpack_from('<IQI', data, 1632)
dtb_size, dtb_addr = struct.unpack_from('<IQ', data, 1648)
assert header_size == 1660 and dtb_addr == 0x47c80000
aligned = lambda size: (size + page - 1) // page * page
assert dtbo_offset == page + aligned(kernel_size) + aligned(ramdisk_size)
dtb_offset = dtbo_offset + aligned(dtbo_size)
assert data[page:page + kernel_size] == (device / 'prebuilt/kernel').read_bytes()
assert data[dtbo_offset:dtbo_offset + dtbo_size] == (device / 'prebuilt/recovery_dtbo').read_bytes()
assert data[dtb_offset:dtb_offset + dtb_size] == (device / 'prebuilt/dtb/mt6833.dtb').read_bytes()
assert data[-64:-60] == b'AVBf'
print('PASS: 128 MiB header v2, load addresses, original kernel/DTB/DTBO and AVB footer.')

archive = gzip.decompress(data[page + aligned(kernel_size):page + aligned(kernel_size) + ramdisk_size])
entries = {}
offset = 0
while True:
    assert offset + 110 <= len(archive), 'Truncated newc header'
    header = archive[offset:offset + 110]
    assert header[:6] == b'070701', 'Unexpected newc format'
    fields = [int(header[index:index + 8], 16) for index in range(6, 110, 8)]
    mode, uid, gid, size, namesize = fields[1], fields[2], fields[3], fields[6], fields[11]
    start = offset + 110
    assert namesize > 0 and start + namesize <= len(archive)
    assert archive[start + namesize - 1] == 0
    name = archive[start:start + namesize - 1].decode()
    start = (start + namesize + 3) // 4 * 4
    assert start + size <= len(archive), 'Truncated newc payload'
    payload = archive[start:start + size]
    offset = (start + size + 3) // 4 * 4
    if name == 'TRAILER!!!':
        assert not any(archive[offset:]), 'Unexpected data after newc trailer'
        break
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts and '\x00' not in name
    name = str(path)
    assert name not in entries, f'Duplicate entry: {name}'
    entries[name] = mode, uid, gid, payload


def read_file(name):
    for _ in range(16):
        mode, _, _, payload = entries[name]
        if not stat.S_ISLNK(mode):
            assert stat.S_ISREG(mode), name
            return payload
        target = payload.decode()
        name = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(name), target))
        assert not name.startswith('../')
    raise AssertionError('Symlink cycle')


for path in (device / 'recovery/root').rglob('*'):
    if path.is_file():
        name = path.relative_to(device / 'recovery/root').as_posix()
        assert read_file(name) == path.read_bytes(), name
for line in (device / 'stock-blob-sha256.txt').read_text().splitlines():
    digest, relative, _ = line.split('  ', 2)
    name = str(PurePosixPath(relative).relative_to('recovery/root'))
    assert hashlib.sha256(read_file(name)).hexdigest() == digest, name
firmware = 'vendor/firmware/tp/21637/FW_NF_ILI9882N_INX.bin'
assert hashlib.sha256(read_file(firmware)).hexdigest() == '329d57276fdab6d0431389f91b77584ac9856987f09feb0a4ba0f5445df9236c'
print('PASS: every device overlay, stock HAL/TEE payload, HAL alias and touch firmware matches the packaged ramdisk.')

for name in ('system/bin/init', 'system/bin/ueventd', 'system/bin/recovery', 'system/bin/adbd', 'system/bin/keystore2', 'system/bin/hwservicemanager', 'system/bin/servicemanager', 'system/bin/fastbootd', 'system/bin/linker64', 'system/lib64/libfscrypt.so', 'system/lib64/libtwrpmtp-ffs.so'):
    payload = read_file(name)
    mode, uid, gid, _ = entries[name]
    assert payload[:5] == b'\x7fELF\x02' and payload[18:20] == b'\xb7\x00', name
    assert uid == 0 and mode & 0o444, name
    if name.startswith('system/bin/'):
        assert mode & 0o111, name
assert entries['init'][3] == b'/system/bin/init'
assert read_file('sepolicy')
ET.fromstring(read_file('vendor/etc/vintf/manifest.xml'))
framework = ET.fromstring(read_file('system/etc/vintf/manifest.xml'))
assert framework.attrib['type'] == 'framework'
manager = framework.find("./hal[name='android.hidl.manager']")
assert manager is not None and manager.findtext('transport') == 'hwbinder'
assert manager.findtext('interface/name') == 'IServiceManager'
assert manager.findtext('interface/instance') == 'default'
ET.fromstring(read_file('twres/ui.xml'))
properties = dict(line.split('=', 1) for line in read_file('prop.default').decode().splitlines() if '=' in line and not line.startswith('#'))
for key, value in {'ro.build.version.release': '16', 'ro.build.version.security_patch': '2026-06-05', 'ro.vendor.build.security_patch': '2026-06-05', 'keymaster_ver': '4.0'}.items():
    assert properties[key] == value, key
assert properties.get('sys.boot_completed') != '1'
assert re.search(rb'^\s+critical\s+window=0\s*$', read_file('system/etc/init/keystore2.rc'), re.MULTILINE), 'Keystore crash protection must remain enabled'
for name, (mode, _, _, payload) in entries.items():
    if stat.S_ISREG(mode) and name.endswith(('.rc', '.sh')):
        assert not re.search(rb'^\s*setprop\s+sys\.boot_completed\s+1\s*(?:#.*)?$', payload, re.MULTILINE), name
print('PASS: required ARM64 executables, fscrypt library, policy, UI, HIDL framework manifest and security patch properties.')
print('PASS: Keystore crash protection is retained; packaged init/shell scripts do not set sys.boot_completed=1.')
print('SHA256:', hashlib.sha256(data).hexdigest())
print('Runtime boot, touch, ADB, partition access and existing-data decryption remain untested.')
