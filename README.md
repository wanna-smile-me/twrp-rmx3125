# TWRP for realme V11s / RMX3125

**TWRP 3.7.1_16-0 非官方适配，针对 RMX3125 真机验证。** 已完成当前 Android 16 环境下的启动、触摸、现有内部存储解密、ADB 和 MTP 测试。适配结果不代表所有 ROM、锁屏凭据或恢复功能均已验证。

## 下载

从 [Releases](https://github.com/wanna-smile-me/twrp-rmx3125/releases/tag/android16-20261023-mtp-zip) 下载 **`RMX3125-TWRP-20261023.zip`**（92,190,593 字节，约 87.9 MiB）。Windows 可直接解压；**刷入解压后的 `.img`，不要直接刷 ZIP 包。**

ZIP SHA-256：`b990ba102d6fbd8df2e591ae9d5a6dccbd2e5371b188c9e031f35e305e865034`。

包内有以下三个文件，解压后已分别与原文件比较 SHA-256，全部一致：

| 文件 | 用途 | 大小 |
| --- | --- | --- |
| `twrp-16-RMX3125-20261023-mtp.img` | 最终 TWRP 镜像 | 128 MiB |
| `stock-recovery-RMX3125.img` | 本次适配使用的原厂 recovery 回退镜像 | 128 MiB |
| `SHA256SUMS.txt` | 两个镜像的 SHA-256 | 文本 |

最终 TWRP SHA-256：

```text
7873cdd834dd61b28267680865a0de04f4ace36cfb656aa05dd6b995ebf9b938
```

原厂 recovery SHA-256：

```text
80fb5e3c6fadb0157daf45772f62dda53ca67faa7d5087b917c33643b8b8d590
```

解压后，在同一目录运行 `sha256sum -c SHA256SUMS.txt`。Windows 也可使用 `Get-FileHash -Algorithm SHA256`。失败的首版和存在 MTP 故障的中间版本没有作为下载成品发布。

## 设备与已测环境

| 项目 | 配置 |
| --- | --- |
| 设备 | realme V11s / RMX3125，MT6833 |
| 分区布局 | A-only，独立 134217728 字节 recovery；动态 system/vendor/product/odm |
| 镜像格式 | Android boot header v2，2048 字节镜像页 |
| 内核 | 复用原厂 recovery 的 4.14.186+ 内核、DTB 和 DTBO |
| 屏幕 | 720 × 1600，ILI9882N INX 触摸固件 |
| 已测系统 | Android 16；系统及 vendor 安全补丁 2026-06-05；vendor API 30 |
| 数据加密 | F2FS、FBE v2 和 metadata encryption；用户 0 现有存储自动解密 |

## 实际验证与限制

2026-10-23 在一台匹配设备上完成以下测试，详见[脱敏验证记录](validation/README.md)：

- TWRP 稳定启动超过五分钟，界面显示和实际触摸正常。
- metadata 和用户 0 CE 数据自动解密，原有内部存储目录可访问；当前凭据状态无需输入 PIN。
- ADB 与 MTP 同时工作。专用 4096 字节文件通过 MTP 传入手机再传回电脑，三处 SHA-256 一致。
- 实际关闭和重新开启 MTP 后，ADB 持续可用，组合 USB 连接正确恢复。
- 正常返回 Android，recovery 分区完整哈希仍与最终镜像一致，专用临时文件已清除。

**未实测**：ZIP 安装、备份还原、格式化、新设置或更改后的 PIN/密码、外置 SD 卡/USB OTG、fastbootd、大文件和长时间 MTP 传输。更换 ROM、安全补丁或凭据后，应重新验证解密。

已知问题：连续批量发送 `twrp get` 查询可能让界面停在操作页面；请避免这样操作，优先使用单次查询或读取公开属性。另请注意，[TWRP 的 Data 备份不包含内部存储中的照片和下载文件](https://twrp.me/faq/backupexclusions.html)，这些应单独备份。

## 使用边界

- 仅用于硬件及分区布局匹配、引导加载程序已解锁的 RMX3125。型号相似不代表兼容。
- 先备份重要数据、核对镜像哈希及回退能力。**镜像目标是 recovery，不是 boot、vbmeta 或 userdata。**
- 本项目实际验证的是写入 recovery 后的启动，不保证 `fastboot boot` 临时启动方式可用。
- 解密失败时不要用格式化或重置凭据来证明兼容。凭据只在手机端输入。
- AVB 使用 AOSP 测试密钥；签名/内容校验通过不等于官方认证，也不保证锁定引导加载程序后可启动。

不提供自动刷机脚本。使用自己的设备序列号，并在操作前检查实际分区和大小。

## 源码与重建

- [设备树](device/realme/RMX3125/BoardConfig.mk)：包含本次使用的原厂预编译内核、固件和硬件加密组件。
- [固定源码清单](manifests/twrp-16-pinned.xml)与[完整本地补丁](patches/README.md)。
- [重建说明](docs/BUILDING.md)、`build-support/` 脚本及根目录 Python 校验工具。
- [组件来源和许可证说明](NOTICE.md)。

本仓库保留适配和重建材料，不包含完整 Android/TWRP 源码、Linux 编译系统或编译缓存。尚未用公开仓库在全新环境中完成一次重建，不承诺镜像逐字节复现。
