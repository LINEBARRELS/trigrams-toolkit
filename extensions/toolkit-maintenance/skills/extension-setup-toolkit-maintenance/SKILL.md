---
name: extension-setup-toolkit-maintenance
description: 声明 toolkit-maintenance 扩展的接入约定与维护路径增量。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# 接入工具包维护扩展

本 Skill 携带 toolkit-maintenance 的[扩展清单](assets/extension.json)、principles 与 workbooks，资源身份沿用 `toolkit-maintenance:*`。在 `core:workbook:project-setup` 的工作 4（扩展管理）中由 Agent 直接按项目路径读取。

## 1. 资源结构与依赖检查

- 确认项目根已由 `harness-install` 装配 `.agents/extensions/toolkit-maintenance/` 快照。
- 本扩展无额外必需领域 Skill，不改变核心成果类型，也不部署项目工具。
- 运行 `handbook validate` 确认扩展快照通过校验，按工作对象可加载对应的维护 workbook（`maintenance-extension`、`maintenance-knowledge`、`maintenance-workbook`、`maintenance-tooling` 或 `maintenance-skill`）。

## 2. 特定目录路径

无固定预设目录；保持 core `docs/` 骨架，不创建空占位目录或文件。

## 3. 项目级文档补充与新增

- **补充现有核心文档**：若项目存在专门的工具包维护源码目录、审核文稿或校验命令，将实际路径、用途与校验命令增量合入 `AGENTS.md`；无专项路径时保持 core 结构不变。
- **按需新增扩展专属文档**：无。
- **移除扩展清理项**：移除本扩展时，从 `AGENTS.md` 摘除仅为工具包维护新增的专属导航与命令条目（保留项目已有文稿与源码）。

## 4. 存量迁移与归档建议（按需）

无领域专属迁移或归档项。
