#!/usr/bin/env bash
set -euo pipefail
test "$(uname -m)" = x86_64
test "$(. /etc/os-release; echo "$VERSION_ID")" = 22.04
sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.ustc.edu.cn/ubuntu/|g; s|http://security.ubuntu.com/ubuntu/|http://mirrors.ustc.edu.cn/ubuntu/|g' /etc/apt/sources.list
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates gnupg curl git python3 python-is-python3 build-essential bc bison flex zip unzip rsync cpio libssl-dev liblz4-tool lzop libncurses5 libxml2-utils xsltproc file xz-utils libelf-dev pkg-config
mkdir -p /opt/bin /opt/twrp /opt/logs
curl --fail --location --retry 2 https://storage.googleapis.com/git-repo-downloads/repo -o /opt/bin/repo
chmod 755 /opt/bin/repo
python3 -m py_compile /opt/bin/repo
git --version
printf 'SETUP_COMPLETE\n'
