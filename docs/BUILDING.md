# 构建记录与重建方法

本说明记录已成功构建所用配置和必要修改。公开整理后的脚本经过语法检查；**尚未在全新环境中执行完整重建**。

## 环境

原环境为 Windows 上的专用 WSL 2 Ubuntu 22.04 x86_64，源码位于 `/opt/twrp`，日志位于 `/opt/logs`。构建目标为 `twrp_RMX3125-bp2a-eng`。本次环境曾占约 86 GB，峰值需求会随缓存、交换文件和源码变化；该数字不是通用的最低空间保证。

`build-support/` 保留本次环境准备、工具链选择、内存控制和检查脚本。它们仍包含专用 WSL 路径、镜像源、网络代理和磁盘保护设置，复用前必须阅读并按实际环境调整。不要在已有的个人开发环境中直接运行安装、同步、工具链裁剪或交换文件管理脚本。

`build-recovery.sh` 及三个相关检查脚本已改为从脚本位置确定项目目录，未保留个人 Windows 路径。其余成功构建参数保持原样：分析阶段两路、编译阶段四路，Soong 内存上限 10 GiB，受检查的临时交换空间及磁盘保护。仓库内没有程序包或完整编译器。

## 恢复源码与补丁

1. 准备所需依赖和 `repo`。所用包列表见 `build-support/setup.sh`；该脚本针对专用 Ubuntu 22.04，会修改其 apt 镜像源。
2. 将本项目放到可由 Linux 访问的位置。以下用 `PROJECT` 表示其绝对目录。
3. 在 `/opt/twrp` 初始化 [TWRP-Test/platform_manifest_twrp_aosp](https://github.com/TWRP-Test/platform_manifest_twrp_aosp) 的 `twrp-16.0` 清单，再使用本仓库 `manifests/twrp-16-pinned.xml` 固定各项目 revision 后同步。只同步移动分支不能保证取得相同源码。

一种配置固定清单的方式如下；按网络与依赖条件调整，**不要在现有有修改的源码树中盲目重做初始化**：

```bash
PROJECT=/absolute/path/to/twrp-rmx3125
mkdir -p /opt/twrp /opt/logs
cd /opt/twrp
repo init -u https://github.com/TWRP-Test/platform_manifest_twrp_aosp.git -b twrp-16.0
cp "$PROJECT/manifests/twrp-16-pinned.xml" .repo/manifests/rmx3125-pinned.xml
repo init -m rmx3125-pinned.xml
repo sync -c --no-tags --no-clone-bundle -j2
repo manifest -r -o /opt/logs/manifest-pinned.xml
```

4. 核对[补丁基准](../patches/README.md)，逐一检查并应用：

```bash
git -C bootable/recovery apply --check "$PROJECT/patches/recovery.patch"
git -C bootable/recovery apply "$PROJECT/patches/recovery.patch"
git -C build/blueprint apply --check "$PROJECT/patches/blueprint.patch"
git -C build/blueprint apply "$PROJECT/patches/blueprint.patch"
git -C build/make apply --check "$PROJECT/patches/build-make.patch"
git -C build/make apply "$PROJECT/patches/build-make.patch"
```

5. 下载并核对本项目 Release 的原厂 recovery，将相同字节保存为 `$PROJECT/stock/recovery.img`。设备树已包含需要的 HAL、TEE、固件及内核载荷，不需要先运行提取工具。
6. 运行 `python3 "$PROJECT/verify_device_tree.py"`。其所需 vendor fstab 基准已保存在 `evidence/fstab.mt6833`。

`prepare_blobs.py` 需要原厂 ramdisk 和解包布局；`register_stock_prebuilts.py` 需要相应构建产物及 AOSP ELF 检查器。它们用于维护预编译组件，不是首次构建前无条件执行的步骤。

## 构建与检查

阅读并适配磁盘/交换空间设置后，使用 `bash "$PROJECT/build-support/build-recovery.sh" all` 完成分析及编译。`compile` 参数用于已核对缓存的恢复编译；真实配置改变仍可能触发完整 Soong 分析。

输出为 `/opt/twrp/out/target/product/RMX3125/recovery.img`。至少运行：

```bash
python3 "$PROJECT/verify_built_image.py" /opt/twrp/out/target/product/RMX3125/recovery.img
sha256sum /opt/twrp/out/target/product/RMX3125/recovery.img
```

随后还需执行 init/VINTF、AVB 签名及内容校验，并按 README 记录的范围进行真机验收。静态工具本身不验证运行兼容性，不能代替实际启动、触摸、现有数据解密和 USB 传输测试。对新产物应记录新的哈希与测试结果，不得沿用旧镜像的验收结论。

## 必须保留的适配

- Android 16 framework HIDL manager/token 声明及硬件加密 HAL 的就绪依赖。
- MTP FunctionFS 挂载、MTP/ADB 双就绪条件及禁用后的第二功能清理。
- MTP AIO 与兼容模式共同的控制端点和描述符初始化。
- 原厂 ELF 的受检查预编译模块、依赖及同字节 HAL 别名；不得跳过 ELF 校验。
- 不在 recovery 中设置 `sys.boot_completed=1`，不移除 Keystore2 的关键崩溃保护。
