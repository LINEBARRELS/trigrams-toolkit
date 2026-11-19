---
name: extension-setup-game
description: 接入 game 扩展时，检查玩法设计、游戏程序开发的资料与项目文稿约定。
metadata:
  harness-toolkit-type: workflow
---

# 接入 game 扩展

本 Skill 携带 game 的[扩展清单](assets/extension.json)、principles 和 workbooks。资源身份沿用 `game:*`。

首次接入与后续增补均从项目已安装的本 Skill 开始。在项目根确认 `harness-install` 已装配 `.agents/extensions/game/`，并检查 `game-designer` 与 `art-designer` 已安装。`handbook` 与 `project-state` 从项目快照发现 `game:*` 资源与类型。

1. 按[文档与路径规范](references/project-integration.md#文档与路径规范)调查现有玩法、研究和表现文稿，确认各路径及读取时机。
2. 按[执行动作与 AGENTS.md 装配](references/project-integration.md#执行动作与-agentsmd-装配)创建有实际内容的文稿和目录，将采用的路径与两级术语导航合并进项目 `AGENTS.md`（首次接入纳入 `initialize` 的目标结构或迁移清单；增补时直接增量合并）。
3. 有旧玩法稿或 GDD 时，按[存量项目迁移](references/project-integration.md#存量项目迁移)整理正式稿、研究草稿与归档，保持延续成果的身份及组合关系。
4. 按[验收要求](references/project-integration.md#验收要求)核对导航、资料可用性和项目状态。
