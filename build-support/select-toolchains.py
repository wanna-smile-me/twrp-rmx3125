"""Apply the six explicitly approved exclusions in this new build environment."""
from pathlib import Path
import re
import shutil
import subprocess

source = Path('/opt/twrp').resolve(strict=True)
clang_config = (source / 'build/soong/cc/config/global.go').read_text()
rust_config = (source / 'build/soong/rust/config/global.go').read_text()
bindgen_config = (source / 'build/soong/rust/bindgen.go').read_text()
assert re.search(r'ClangDefaultVersion\s*=\s*"clang-r547379"', clang_config)
assert re.search(r'RustDefaultVersion\s*=\s*"1.83.0"', rust_config)
assert 'bindgenClangVersion = "clang-r530567"' in bindgen_config

projects = {
    'prebuilts/clang/host/linux-x86': ['clang-r522817', 'clang-r536225'],
    'prebuilts/rust': ['linux-x86/1.82.0', 'darwin-x86', 'windows-x86', 'linux-musl-x86/1.82.0'],
}
reference = 'refs/tags/android-16.0.0_r1'
for relative, exclusions in projects.items():
    worktree = source / relative
    gitdir = (source / '.repo/projects' / (relative + '.git')).resolve(strict=True)
    assert gitdir.is_relative_to(source / '.repo')
    git = ['git', f'--git-dir={gitdir}', f'--work-tree={worktree}']
    subprocess.run(git + ['rev-parse', '--verify', reference], check=True, stdout=subprocess.DEVNULL)
    patterns = '/*\n' + ''.join(f'!/{name}/\n' for name in exclusions)
    info = (gitdir / 'info').resolve(strict=True)
    assert info.is_relative_to(source / '.repo')
    (info / 'sparse-checkout').write_text(patterns)
    subprocess.run(git + ['config', 'core.sparseCheckout', 'true'], check=True)
    subprocess.run(git + ['config', 'core.sparseCheckoutCone', 'false'], check=True)
    for name in exclusions:
        path = worktree / name
        resolved = path.resolve()
        assert resolved.is_relative_to(worktree.resolve()) and not path.is_symlink()
        if path.exists():
            shutil.rmtree(path)
            print(f'Removed approved old toolchain: {resolved}', flush=True)
    # Restore the interrupted initial checkout from its unchanged, cached AOSP tag.
    subprocess.run(git + ['read-tree', '--reset', '-u', reference], check=True)
    subprocess.run(git + ['diff', '--quiet', reference, '--'], check=True)
    assert all(not (worktree / name).exists() for name in exclusions)

clang = source / 'prebuilts/clang/host/linux-x86'
assert (clang / 'clang-r530567').is_dir()
subprocess.run([str(clang / 'clang-r547379/bin/clang'), '--version'], check=True)
subprocess.run([str(source / 'prebuilts/rust/linux-x86/1.83.0/bin/rustc'), '--version'], check=True)
assert (source / 'prebuilts/rust/linux-musl-x86/1.83.0/bin/rustc').is_file()
print('PASS: approved exclusions absent, selected toolchains restored and executable.', flush=True)
