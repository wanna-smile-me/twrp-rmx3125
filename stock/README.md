# 原厂 recovery 基准

原厂 recovery 放在 [Release 的 ZIP 包](https://github.com/wanna-smile-me/twrp-rmx3125/releases/tag/android16-20261023-mtp-zip)中。下载并解压 `RMX3125-TWRP-20261023.zip` 后得到 `stock-recovery-RMX3125.img`；镜像不直接存入 Git 历史。

- 大小：134217728 字节。
- SHA-256：`80fb5e3c6fadb0157daf45772f62dda53ca67faa7d5087b917c33643b8b8d590`。
- 用途：本次设备树的原厂内核/DTB/DTBO 比对基准，以及匹配设备 recovery 分区的回退材料。

运行根目录设备树校验工具前，将下载并核对后的相同字节保存为本目录 `recovery.img`。该文件已被 `.gitignore` 排除。

它不是 boot 镜像，也不是整机或 userdata 备份，不适用于其他型号或任意不同固件。恢复 recovery 不能保证撤销之前的凭据、密钥或数据变化。
