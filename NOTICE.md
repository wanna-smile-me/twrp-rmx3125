# 来源与组件许可证

本项目是设备适配、构建记录和镜像分发，不是 TeamWin 官方发布。各组件保留原著作权及许可证，不能将整个镜像视为同一许可证的原创作品。

- **TWRP**：源码清单为 [TWRP-Test/platform_manifest_twrp_aosp](https://github.com/TWRP-Test/platform_manifest_twrp_aosp)，本次分支 `twrp-16.0`。Recovery 基准为 [0315dbb53c47a0532546b7056f6af71b4dc0ddab](https://github.com/TWRP-Test/android_bootable_recovery/tree/0315dbb53c47a0532546b7056f6af71b4dc0ddab)；本地修改完整保存在 `patches/recovery.patch`。其上游 [NOTICE 副本](licenses/TWRP-NOTICE.txt)包含 GPLv3 或后续版本声明。其他源码文件可能有独立许可，应依文件原声明处理。
- **MTP/AOSP 与构建系统**：保留 Android Open Source Project / Google 及其他原作者的版权声明。[MTP NOTICE](licenses/MTP-NOTICE.txt)和 [Apache License 2.0](licenses/Apache-2.0.txt)一并保留。Blueprint 和 build/make 基准及本地补丁见 `patches/README.md`；其余源码 revision 见固定清单。
- **内核**：镜像直接复用原厂 recovery 中的 4.14.186+ 内核载荷，没有在本次 TWRP 构建中重新编译内核。厂商公开源码仓库为 [realme_V11_V11S-AndroidR-kernel-source](https://github.com/realme-kernel-opensource/realme_V11_V11S-AndroidR-kernel-source)，其 [COPYING 副本](licenses/kernel-COPYING.txt)随附。本项目没有验证该仓库重建结果与原厂载荷逐字节相同，不将其描述为本次预编译内核的重建验证。
- **原厂二进制**：内核/DTB/DTBO、触摸固件、Trustonic/MediaTek/厂商 HAL 和 TEE 组件来自本次适配使用的原厂 recovery。它们不是本项目自行编写的代码，本仓库不为这些组件重新授予开源许可证。`device/realme/RMX3125/stock-blob-sha256.txt` 记录原厂 ELF 来源及哈希。
- **设备配置**：现有文件中的 TeamWin/AOSP 著作权和 SPDX 声明保留。没有标注统一许可证的新说明或辅助文件，不构成对第三方组件的重新许可。

完整 TWRP/AOSP 来源由 [固定清单](manifests/twrp-16-pinned.xml)和本地补丁共同描述。AVB 使用上游 AOSP 测试密钥，仓库不包含个人私钥、锁屏凭据或用户数据。
