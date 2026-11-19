# Codex Adapter

core 项目安装按所选平台将两个角色入口复制到项目 `.codex/agents/`，分别调用 `execute-task` 与 `delivery-review` Skill，无需启用领域扩展。

`src/trigrams_toolkit/resources/adapters/codex/` 是配置唯一来源，安装器按已确认预览将角色入口复制到 `.codex/agents/`。公共 CLI 与 core Skill 分别由统一 Python 包（`uv tool install`）和 Vercel skills 全局安装，项目扩展 Skill 与资源快照分别由 Vercel skills 与 `harness-install` 装配；项目不预装 Plan 工具。全局安装方式向 `toolkit-steward` 查询，项目配置与扩展管理方法通过 `handbook load core:workbook:project-setup` 加载。

默认沿用会话模型与推理设置；项目固定模型时，在平台入口保存实际可用配置。角色使用 workspace-write，工作边界由 Task 与 Skill 确定。在新会话核对实际角色发现，当前会话不会自动刷新。

当前安装中断时，读取 `core:workbook:project-setup` 的装配说明并按其中的归档回退方法恢复。配套材料相对 `handbook load` 返回的 `entryPath` 定位。
