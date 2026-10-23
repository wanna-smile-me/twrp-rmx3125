"""Seed the unchanged AOSP objects before Repo fetches the TWRP forks."""
from pathlib import Path
import os
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

source = Path('/opt/twrp')
sys.path.insert(0, str(source / '.repo/repo'))
from manifest_xml import RepoClient

# shortcut: uses Repo 2.69's repository initialization API; recheck before upgrading Repo.
client = RepoClient(str(source / '.repo'))
original = ET.parse(source / '.repo/manifests/default.xml')
paths = {p.get('path', p.get('name')): p.get('name') for p in original.findall('project')}
limit = 52 * 1024 ** 3

for project in client.projects:
    if not project.remote.url.startswith('https://github.com/TWRP-Test/') or project.relpath not in paths:
        continue
    check = subprocess.run(['git', f'--git-dir={project.gitdir}', 'rev-parse', '--verify', f'refs/remotes/{project.remote.name}/twrp-16.0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode == 0:
        continue
    project._InitGitDir()
    url = 'https://mirrors.ustc.edu.cn/aosp/' + paths[project.relpath]
    print(f'SEED_START {project.relpath}', flush=True)
    with open('/opt/logs/aosp-seed.log', 'a') as log:
        process = subprocess.Popen(['git', f'--git-dir={project.gitdir}', 'fetch', '--depth=1', '--no-tags', url, 'refs/tags/android-16.0.0_r1:refs/tags/aosp-seed'], stdout=log, stderr=log, start_new_session=True)
        while process.poll() is None:
            usage = os.statvfs('/')
            if (usage.f_blocks - usage.f_bfree) * usage.f_frsize >= limit:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait()
                raise RuntimeError('Source seeding reached the approved space guard')
            time.sleep(2)
        if process.returncode:
            raise RuntimeError(f'AOSP seed fetch failed for {project.relpath}; see /opt/logs/aosp-seed.log')
    print(f'SEED_DONE {project.relpath}', flush=True)
print('AOSP_SEED_COMPLETE', flush=True)
