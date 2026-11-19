---
name: extension-setup-game
description: 仅在用户显式调用或由 project-setup 按项目路径读取时使用；声明 game 扩展的接入约定、目录路径与存量迁移增量。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# 接入 game 扩展

本 Skill 携带 game 的[扩展清单](assets/extension.json)、principles 与 workbooks，资源身份沿用 `game:*`。在 `core:workbook:project-setup` 的扩展管理步骤中由 Agent 直接按项目路径读取。

1. 在项目根确认 `harness-install` 已装配 `.agents/extensions/game/`，且项目已安装 `game-designer` 与 `art-designer`。`handbook` 与 `project-state` 从项目快照发现 `game:*` 资源与类型。
2. 按[文档与路径规范](references/project-integration.md#文档与路径规范)确定项目采用的玩法、研究与表现文稿路径。
3. 按[执行动作与 AGENTS.md 装配](references/project-integration.md#执行动作与-agentsmd-装配)将采用的路径与两级术语路由并入 `project-setup` 的目录骨架与 `AGENTS.md` 收敛步骤。
4. 存在旧玩法稿或 GDD 时，按[存量项目迁移](references/project-integration.md#存量项目迁移)纳入 `project-setup` 工作 5 的迁移与归档建议清单。
5. 按[验收要求](references/project-integration.md#验收要求)核对导航、资料可用性与项目状态。
