---
name: extension-setup-game
description: 声明 game 扩展的接入约定、目录路径、文档增量与存量迁移建议。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# 接入 game 扩展

本 Skill 携带 game 的[扩展清单](assets/extension.json)、principles 与 workbooks，资源身份沿用 `game:*`。在 `core:workbook:project-setup` 的工作 4（扩展管理）与工作 5（仅用户明确要求时）中由 Agent 直接按项目路径读取。详细规范见[game 扩展接入说明](references/project-integration.md)。

## 1. 资源结构与依赖检查

- 确认项目根已由 `harness-install` 装配 `.agents/extensions/game/` 快照。
- 确认项目已通过 Vercel skills 安装 `extension-setup-game`、`game-designer` 与 `art-designer`。
- 运行 `handbook validate` 核对 `game:*` 资源可用；`project-state` 从快照自动发现 `game:gameplay-spec` 成果类型与 `game:composes` 关系类型。

## 2. 特定目录路径

在核心 `docs/` 骨架上按需补充以下领域目录（不创建无实际内容的空正文）：

- `docs/gameplays/`：正式定稿的 `gameplay-spec`。
- `docs/research/gameplay/<topic>/`：按主题归集的玩法探索草稿（不登记正式 Registry）。

## 3. 项目级文档补充与新增

- **补充现有核心文档**：
  - `PRODUCT.md`：按需补充阶段体验、版本目标与跨玩法全局业务术语。
  - `DESIGN.md`：承载游戏 UI／UX、操作映射、HUD 布局与交互表达。
  - `AGENTS.md`：在“项目结构”合入实际存在的 `DESIGN.md`、`docs/GAME-VISUALS.md`、`docs/gameplays/` 与 `docs/research/gameplay/`；在“项目术语 → 术语检索说明”合并两级路由（全局业务术语 → `PRODUCT.md`，玩法局部术语 → `docs/gameplays/` 对应 Spec）。
- **按需新增扩展专属文档**：
  - `docs/GAME-VISUALS.md`：仅在明确需要游戏视觉与表现规范时创建，维护世界、角色、视觉语言、镜头、光影与场景可读性。
- **移除扩展清理项**：移除 `game` 扩展时，从 `AGENTS.md` 摘除上述游戏专属导航与局部玩法术语路由（保留项目已有文稿与正式成果）。

## 4. 存量迁移与归档建议（按需）

仅在用户明确要求执行 `project-setup` 工作 5 时读取[存量项目迁移](references/project-integration.md#存量项目迁移)，将旧 `docs/gameplay-specs/` 归位、旧大部头 GDD 拆解与 `docs/archives/game-designs/` 归档建议并入 `migration/checklist.md`。
