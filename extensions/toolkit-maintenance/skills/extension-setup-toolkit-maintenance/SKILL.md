---
name: extension-setup-toolkit-maintenance
description: 仅在用户显式调用或由 project-setup 按项目路径读取时使用；声明 toolkit-maintenance 扩展的接入约定与维护路径增量。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# 接入工具包维护扩展

本 Skill 携带 toolkit-maintenance 的[扩展清单](assets/extension.json)、principles 与 workbooks，资源身份沿用 `toolkit-maintenance:*`。在 `core:workbook:project-setup` 的扩展管理步骤中由 Agent 直接按项目路径读取。

1. **确认项目装配**：在项目根确认 `harness-install` 已装配 `.agents/extensions/toolkit-maintenance/`。本扩展不预设固定项目文档目录，不改变核心成果类型，也不部署项目工具。
2. **合并实际维护路径**：若项目存在专门的维护源码目录、审核文稿或校验命令，将实际路径、用途与读取时机并入 `project-setup` 的 `AGENTS.md` 收敛步骤；无专项维护路径时保持 core 结构，不创建空占位文件。
3. **验证与加载**：运行 `handbook validate` 确认扩展快照通过校验，随后按工作对象加载对应 workbook：`maintenance-extension`、`maintenance-knowledge`、`maintenance-workbook`、`maintenance-tooling` 或 `maintenance-skill`。
