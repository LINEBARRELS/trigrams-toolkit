```text
图难于其易，为大于其细。
```

![水墨山雾中，白衣龙娘在山崖上运功，墨迹随掌势展开](docs/assets/trigrams-banner.webp)

# Trigrams toolkit

面向软件与游戏工程的 **Agent 工具包**。把工程判断与工作方法沉淀成可复用的资料，用 Plan 与 Task 组织多阶段工作、角色交接和交付验收。

[![PyPI 版本](https://img.shields.io/pypi/v/trigrams-toolkit?style=flat&label=PyPI&color=386964)](https://pypi.org/project/trigrams-toolkit/)
[![MIT License](https://img.shields.io/badge/license-MIT-386964?style=flat)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-386964?style=flat)](pyproject.toml)

[快速开始](#快速开始) · [体系架构](skills/toolkit-steward/references/architecture.md) · [官方扩展](#官方扩展) · [参与开发](CONTRIBUTING.md)

## 快速开始

准备好 `uv`、Python 3.11+ 和用于运行 `npx` 的 Node.js。

### 安装全局工具

```sh
# 安装或升级四个全局 CLI（project-state、plan-toolkit、handbook、harness-install）
uv tool install -U trigrams-toolkit

# 全局安装 core Skill（含 toolkit-steward）及随附的 workbook 和 principle
npx skills add LINEBARRELS/trigrams-toolkit/skills --skill '*' -g
```

### 接入目标项目

在目标项目中打开 Agent，粘贴下面这段话。

```text
请用 toolkit-steward 帮我把 Trigrams toolkit 安装到这个项目。
先看看仓库现在是怎么组织的，不破坏现有内容，按需把缺的配置、目录和项目文档补齐。
开始前先简单告诉我要改什么、接下来怎么用。
```

## 设计哲学

![雨后梯田里，穿靛青汉服的猫娘移开石板，水从田埂缺口流入下一畦](docs/assets/trigrams-terraces.webp)

### 复用判断与工作方法

<sub>以爻成卦</sub>

**principle** 提供判断标准，**workbook** 定义工作方法。Agent 按任务加载所需资料。比如新功能和重构可以沿用同一条验证原则，各自用 workbook 约定工作步骤和交接要求。

### 用 Plan 和 Task 组织交付

<sub>随势布阵</sub>

**Plan** 明确目标和任务依赖，**Task** 写清工作依据、交付物和验收条件。前置任务完成后再推进依赖它的工作，独立任务可以并行。交付时，根据产物和验证证据审核结果。单步工作可直接调用对应的 Skill。

## Core Skill

Skill 定义 Agent 的行为。公共 CLI 提供资料检索、计划查询、状态登记和扩展装配。官方扩展在项目中补充领域能力。

| 要做的事 | Core Skill |
| --- | --- |
| **接入项目，加载工作依据** | [`toolkit-steward`](skills/toolkit-steward/SKILL.md) · [`workbook`](skills/workbook/SKILL.md) · [`principles`](skills/principles/SKILL.md) |
| **调查现状，推敲设计** | [`how`](skills/how/SKILL.md) · [`why`](skills/why/SKILL.md) · [`effect`](skills/effect/SKILL.md) · [`architect`](skills/architect/SKILL.md) |
| **规划工作，执行与审核交付** | [`to-plan`](skills/to-plan/SKILL.md) · [`execute-plan`](skills/execute-plan/SKILL.md) · [`execute-task`](skills/execute-task/SKILL.md) · [`delivery-review`](skills/delivery-review/SKILL.md) |
| **维护文档、原则与决策** | [`doc-polish`](skills/doc-polish/SKILL.md) · [`principle-maintenance`](skills/principle-maintenance/SKILL.md) · [`decision-maintenance`](skills/decision-maintenance/SKILL.md) |

<details>
<summary>公共 CLI 与协议</summary>

| 工具 | 职责 |
| --- | --- |
| [`handbook`](src/trigrams_toolkit/resources/handbook/PROTOCOL.md) | 检索、加载和校验 workbook 与 principle |
| [`plan-toolkit`](src/trigrams_toolkit/resources/plan/PROTOCOL.md) | 读取计划快照，查询依赖、可运行任务和当前状态 |
| [`project-state`](src/trigrams_toolkit/resources/state/PROTOCOL.md) | 登记和查询架构实体、成果及其关系 |
| [`harness-install`](src/trigrams_toolkit/resources/installation/PROTOCOL.md) | 预览并装配扩展快照与宿主角色入口 |

</details>

## 官方扩展

- **[game](extensions/game/README.md)** 为游戏项目提供玩法设计、美术与 UI 规范，以及配套的 workbook 和 principle。
- **[toolkit-maintenance](extensions/toolkit-maintenance/README.md)** 为开发和维护工具包提供扩展开发、知识库、工作方法维护、工具部署与 Skill 审核规程。

官方扩展按项目启用。项目快照固定所用的扩展资料，后续可用 `harness-install` 预览并同步。安装步骤见[目标安装与项目接入](docs/getting-started.md#目标安装与项目接入)。

## 深入了解

- **设计与决策**　[体系架构](skills/toolkit-steward/references/architecture.md) · [项目决策索引](docs/knowledge/decisions/index.md)
- **开发与维护**　[开发环境](docs/getting-started.md) · [参与开发](CONTRIBUTING.md) · [维护与发布](docs/maintenance.md) · [更新记录](CHANGELOG.md)
- **许可**　[MIT License](LICENSE) · [第三方内容声明](THIRD_PARTY_NOTICES.md)
