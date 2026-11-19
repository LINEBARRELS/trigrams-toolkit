---
name: extension-setup-toolkit-maintenance
description: 接入 toolkit-maintenance 扩展时，检查工具包开发、资料维护与审核所需的工作方法和原则。
metadata:
  harness-toolkit-type: workflow
---

# 接入工具包维护扩展

本 Skill 携带 toolkit-maintenance 的[扩展清单](assets/extension.json)、principles 和 workbooks。资源身份沿用 `toolkit-maintenance:*`。

首次接入和后续增补均从项目已安装的本 Skill 开始：

1. **确认项目装配**。在项目根确认 `harness-install` 已装配 `.agents/extensions/toolkit-maintenance/`。本扩展不预设固定项目文档目录，不改变核心成果类型，也不部署项目工具。
2. **合并实际维护路径**：若项目采用专门的维护源码目录、审核文稿或校验命令，将实际路径、用途与读取时机合并进项目 `AGENTS.md`（首次接入纳入 `initialize` 的目标结构或迁移清单，增补时直接增量合并）；无专项维护路径时保持 core 结构，不创建空占位文件。
3. **验证与加载**：运行 `handbook validate` 确认扩展快照通过校验，随后按工作对象加载对应 workbook：`maintenance-extension`、`maintenance-knowledge`、`maintenance-workbook`、`maintenance-tooling` 或 `maintenance-skill`。
