# 真机验收证据 — 2026-10-23

这些是本次实际测试日志的脱敏副本：设备序列号、Windows USB 实例标识和个人主机项目路径已替换。未发布凭据、私人文件、无关诊断日志或旧 framebuffer 截图。时间为测试主机记录的 Asia/Shanghai 时间；恢复环境自身时间可能不同。

| 检查 | 日志 |
| --- | --- |
| 唯一 recovery 分区写入、写前/写后哈希 | [flash](mtp-final-flash-20261023.log) |
| 启动、加密服务、现有 metadata/CE 解密及 USB 枚举 | [runtime](mtp-final-runtime-20261023.log) |
| 4096 字节文件经真正 MTP 双向传输、哈希及清理 | [roundtrip](mtp-final-roundtrip-20261023.log) |
| 用户触摸操作 MTP 开关、ADB 保留及重新连接 | [toggle](mtp-final-toggle-20261023.log) |
| 正常 Android 启动完成及 recovery 保留 | [return-normal](mtp-final-return-normal-20261023.log) |
| 实际交付镜像结构、载荷及设备配置检查 | [static](mtp-ffs-copied-image-static-20261023.log) |
| 实际交付镜像 AVB 签名及分区 hash descriptor | [AVB](mtp-final-avb-verify.txt) |
| 最终构建成功、MTP 源码编译和链接 | [build](mtp-ffs-build-success-20261023-1306.log) |

只传输了预先确定内容的专用测试文件，未传输私人文件。其 SHA-256 为 `c8f5d0341d54d951a71b136e6e2afcb14d11ed8489a7ae126a8fee0df6ecf193`。

静态校验脚本打印的“运行功能未测试”描述的是该工具本身不做运行测试；独立真机结果见上述运行日志。本次解密验证针对用户 0 当前默认凭据状态，没有通过新设置或更改 PIN 来验证其他凭据状态。ZIP 安装、备份还原、格式化、外置存储、fastbootd 及大文件/长期传输未实测。
