"""Static checks for the physical RMX3125; these do not establish runtime compatibility."""
import hashlib
from pathlib import Path
import struct
import re
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parent
device = base / 'device/realme/RMX3125'
stock = (base / 'stock/recovery.img').read_bytes()
assert hashlib.sha256(stock).hexdigest() == '80fb5e3c6fadb0157daf45772f62dda53ca67faa7d5087b917c33643b8b8d590'
assert stock[:8] == b'ANDROID!'
kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, _, tags_addr, page, version = struct.unpack_from('<9I', stock, 8)
assert (kernel_addr, ramdisk_addr, tags_addr, page, version) == (0x40080000, 0x51100000, 0x47c80000, 2048, 2)
dtbo_size, dtbo_offset, header_size = struct.unpack_from('<IQI', stock, 1632)
dtb_size, dtb_addr = struct.unpack_from('<IQ', stock, 1648)
assert header_size == 1660 and dtb_addr == 0x47c80000
aligned = lambda size: (size + page - 1) // page * page
dtb_offset = page + aligned(kernel_size) + aligned(ramdisk_size) + aligned(second_size) + aligned(dtbo_size)
assert (device / 'prebuilt/kernel').read_bytes() == stock[page:page + kernel_size]
assert (device / 'prebuilt/recovery_dtbo').read_bytes() == stock[dtbo_offset:dtbo_offset + dtbo_size]
assert (device / 'prebuilt/dtb/mt6833.dtb').read_bytes() == stock[dtb_offset:dtb_offset + dtb_size]
firmware = device / 'recovery/root/vendor/firmware/tp/21637/FW_NF_ILI9882N_INX.bin'
assert hashlib.sha256(firmware.read_bytes()).hexdigest() == '329d57276fdab6d0431389f91b77584ac9856987f09feb0a4ba0f5445df9236c'
for line in (device / 'stock-blob-sha256.txt').read_text().splitlines():
    digest, relative, _ = line.split('  ', 2)
    assert hashlib.sha256((device / relative).read_bytes()).hexdigest() == digest, relative
elf_paths = {line.split('  ', 2)[1] for line in (device / 'stock-blob-sha256.txt').read_text().splitlines()}
installed_elf_paths = set()
module_names = set()
dependencies = set()
for block in (device / 'Android.mk').read_text().split('include $(CLEAR_VARS)')[1:]:
    properties = dict(re.findall(r'^(LOCAL_\w+) := *(.*)$', block, re.MULTILINE))
    source = properties['LOCAL_SRC_FILES']
    assert source in elf_paths and source not in installed_elf_paths, source
    assert properties['LOCAL_CHECK_ELF_FILES'] == 'true'
    assert properties['LOCAL_STRIP_MODULE'] == 'false'
    assert properties['LOCAL_MULTILIB'] == '64'
    destination = properties['LOCAL_MODULE_PATH'].replace('$(TARGET_RECOVERY_ROOT_OUT)', 'recovery/root')
    filename = properties['LOCAL_MODULE_STEM'] + properties.get('LOCAL_MODULE_SUFFIX', '')
    assert f'{destination}/{filename}' == source, source
    installed_elf_paths.add(source)
    module_names.add(properties['LOCAL_MODULE'])
    dependencies.update(properties.get('LOCAL_SHARED_LIBRARIES', '').split())
    for alias in properties.get('LOCAL_MODULE_SYMLINKS', '').split():
        alias_path = f'{destination}/{alias}'
        assert alias_path in elf_paths
        assert (device / alias_path).read_bytes() == (device / source).read_bytes()
        installed_elf_paths.add(alias_path)
assert installed_elf_paths == elf_paths, 'Unregistered stock ELF payload'
assert dependencies <= module_names | {'libc.recovery', 'libm.recovery', 'libdl.recovery'}
package_names = set(re.findall(r'rmx3125_stock_\w+', (device / 'stock-prebuilts.mk').read_text()))
assert package_names == module_names, 'Stock module package list mismatch'
product = (device / 'twrp_RMX3125.mk').read_text()
assert '$(filter-out' in product
assert '$(LOCAL_PATH)/recovery/root/vendor/bin/%' in product
assert '$(LOCAL_PATH)/recovery/root/vendor/lib64/%' in product
assert '$(call inherit-product, device/realme/RMX3125/stock-prebuilts.mk)' in product
fstab = (device / 'recovery/root/system/etc/recovery.fstab').read_text()
live_fstab = (base / 'evidence/fstab.mt6833').read_text(encoding='utf-8-sig')
data_options = next(line.split()[-1] for line in fstab.splitlines() if line.startswith('/dev/block/by-name/userdata '))
live_options = next(line.split()[-1] for line in live_fstab.splitlines() if line.startswith('/dev/block/by-name/userdata '))
for option in live_options.split(','):
    if option.startswith(('fileencryption=', 'keydirectory=')):
        assert option in data_options.split(','), option
board = (device / 'BoardConfig.mk').read_text()
assert 'BOARD_RECOVERYIMAGE_PARTITION_SIZE := 134217728' in board
assert 'BOARD_BOOT_HEADER_VERSION := 2' in board
assert 'permissive' not in board and 'disable_verification' not in board
ET.parse(device / 'recovery/root/vendor/etc/vintf/manifest.xml')
root = device / 'recovery/root'
framework_path = root / 'system/etc/vintf/manifest.xml'
assert framework_path.is_file(), 'Missing framework manifest required by Android 16 hwservicemanager'
framework = ET.parse(framework_path).getroot()
assert framework.attrib['type'] == 'framework'
manager = framework.find("./hal[name='android.hidl.manager']")
assert manager is not None and manager.findtext('transport') == 'hwbinder'
assert manager.findtext('interface/name') == 'IServiceManager'
assert manager.findtext('interface/instance') == 'default'
init_text = (root / 'init.recovery.mt6833.rc').read_text()
crypto_action = next(block for block in re.split(r'(?m)^on ', init_text)[1:]
                     if re.search(r'^    start keymaster-4-0$', block, re.MULTILINE))
ready_properties = {'hwservicemanager.ready': 'true', 'init.svc.mobicore': 'running'}
triggers = re.findall(r'property:([^=\s]+)=(\S+)', crypto_action.splitlines()[0])
assert triggers and all(ready_properties.get(name) == value for name, value in triggers), 'Hardware HALs must start before data encryption can be detected'
usb_actions = re.split(r'(?m)^on ', init_text)[1:]
mtp_action = next(block for block in usb_actions if '    symlink /config/usb_gadget/g1/functions/ffs.mtp ' in block)
assert dict(re.findall(r'property:([^=\s]+)=(\S+)', mtp_action.splitlines()[0])) == {
    'sys.usb.config': 'mtp,adb', 'sys.usb.ffs.ready': '1',
    'sys.usb.ffs.mtp.ready': '1', 'sys.usb.configfs': '1',
}, 'Bind composite USB only after both FunctionFS descriptor sets are ready'
assert '    mount functionfs mtp /dev/usb-ffs/mtp uid=0,gid=0' in init_text
assert '    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f2' in mtp_action
none_action = next(block for block in usb_actions if block.splitlines()[0] == 'property:sys.usb.config=none && property:sys.usb.configfs=1')
assert '    rm /config/usb_gadget/g1/configs/b.1/f2' in none_action, 'Remove the second USB function before returning to ADB'
for rc in root.glob('init.recovery*.rc'):
    text = rc.read_text()
    for path in re.findall(r'^service\s+\S+\s+(/\S+)|-r\s+(/\S+)|^import\s+(/\S+)', text, re.MULTILINE):
        relative = next(value for value in path if value).lstrip('/')
        assert (root / relative).is_file(), f'Missing init dependency: {relative}'
print('PASS: stock identity, kernel/DTB/DTBO, touch firmware, HAL hashes, encryption options, image size and manifest syntax.')
print('PASS: device init imports, service executables and Trustonic driver files exist.')
print('PASS: stock ELFs use checked prebuilt modules with complete dependencies, packages and HAL aliases.')
print('PASS: framework HIDL manager is declared and crypto HAL startup does not depend on detecting encrypted data.')
print('PASS: MTP uses FunctionFS with both readiness conditions, composite ADB and second-function cleanup.')
print('Runtime boot, touch, mounts and decryption remain untested.')
