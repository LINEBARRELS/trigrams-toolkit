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

1. **安装全局 CLI 与 core Skill。**

   ```sh
   uv tool install -U trigrams-toolkit
   npx skills add LINEBARRELS/trigrams-toolkit/skills --skill '*' -g
   ```

2. **接入目标项目。** 在目标项目中，请 Agent 使用 [`toolkit-steward`](skills/toolkit-steward/SKILL.md) 按 [`project-setup` workbook](skills/workbook/workbooks/project-setup/WORKBOOK.md) 核对基础配置、建立目录骨架并维护项目文档。已有项目可从核对现状开始。

<details>
<summary>Claude Code 与安装排查</summary>

使用 Claude Code 时，可在 `npx skills add` 命令末尾附加 `-a claude-code`。CLI 的帮助与版本可在任意目录查看。`handbook`、`plan-toolkit` 和 `project-state` 可从项目子目录识别项目根，`harness-install` 在当前目录装配。

参阅[全局安装与恢复指引](skills/toolkit-steward/references/deployment.md)或[开发与接入指南](docs/getting-started.md)。

</details>

## 设计哲学

### 以爻成卦

一爻虽简，入于不同卦位，自有不同用处。**principle** 提供判断标准，**workbook** 定义工作方法。Agent 按当前工作加载所需资料，workbook 也可复用其他 workbook 和 principle。新增一种工作时，已有的判断与方法仍可独立使用。

### 随势布阵

布阵先定方位，再定进退。**Plan** 统筹目标与依赖，**Task** 约定依据、产物和验收。开发者按依赖安排先后，把独立任务交给执行者并行推进，再凭产物和证据审核交付。单步工作可直接调用对应的 Skill。

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
