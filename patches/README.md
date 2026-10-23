# 本地源码补丁

三份补丁均从实际成功构建树相对 HEAD 完整导出；导出时 HEAD 与固定清单匹配，且全部通过 `git apply --reverse --check`。设备树修改单独保存在 `device/realme/RMX3125/`。

| 仓库 | 基准 revision | 补丁 |
| --- | --- | --- |
| `bootable/recovery` | `0315dbb53c47a0532546b7056f6af71b4dc0ddab` | [recovery.patch](recovery.patch) |
| `build/blueprint` | `dcb14f2e146f40cf1f212efb220e9aa1f3cfc280` | [blueprint.patch](blueprint.patch) |
| `build/make` | `74715e25d7c2ede6ae00db69d08970e3cf81c20c` | [build-make.patch](build-make.patch) |

- Recovery：将已有描述符初始化移到 AIO 和兼容模式共享的端点打开路径，修复兼容模式下缺少数据端点的问题。
- Blueprint：限制模块处理和 provider 验证并行度，适应本次内存条件，保留检查并包含对应测试修改。
- Build/make：配置 JSON 内容不变时保留原文件及时间戳，内容改变时正常更新，不伪造时间戳。

完整源码来源及 revision 见 [twrp-16-pinned.xml](../manifests/twrp-16-pinned.xml)。这些补丁适用于上述基准，不能直接假定适用于其他分支或版本。
