<div align="center">

`图难于其易，为大于其细。`

![水墨山雾中，白衣龙娘在山崖上运功，墨迹随掌势展开](docs/assets/trigrams-banner.webp)

# Trigrams toolkit

面向各类工作的 **Agent 工具包**。<br>
用 Plan 组织多步工作、角色交接和交付验收，按需复用判断标准与工作方法。

[![CLI PyPI 版本](https://img.shields.io/pypi/v/trigrams-toolkit?style=flat&label=CLI%20PyPI&color=386964)](https://pypi.org/project/trigrams-toolkit/)
[![MIT License](https://img.shields.io/badge/license-MIT-386964?style=flat)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-386964?style=flat)](pyproject.toml)

[快速开始](#快速开始) · [Plan 如何工作](#plan-如何工作) · [官方扩展](#官方扩展) · [参与开发](CONTRIBUTING.md)

</div>

## 快速开始

准备好 `uv`、Python 3.11+ 和用于运行 `npx` 的 Node.js。

### 安装全局工具

```sh
# 安装或升级全局 CLI
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

### 跑通第一份 Plan

把定稿的设计文档交给 Agent，用 `/to-plan` 制定计划。下面以博物馆更新导览路线为例，规划范围从一场试行开始。

```text
/to-plan 根据 `docs/博物馆导览路线设计.md` 制定计划。
先选一场周末导览试行，沿用现有志愿者排班。试行结束后汇总现场反馈，交给馆方负责人决定是否推广。
```

确认计划后，调用 `/execute-plan` 执行。

```text
/execute-plan 执行刚生成的 Plan。
```

![雨后梯田里，穿靛青汉服的猫娘移开石板，水从田埂缺口流入下一畦](docs/assets/trigrams-terraces.webp)

## Plan 如何工作

<sub>随势布阵</sub>

Plan 将多步工作拆成可独立验收的交付单元（Stub）。Agent 按依赖安排交付与独立审核，最后验收整份 Plan。单步工作可直接调用对应的 Skill。

<details>
<summary>查看 Plan 的文件结构</summary>

| 路径 | 内容 |
| --- | --- |
| `summary.md` | 工作目标、验收标准、生效规则与 Stub 清单 |
| `Sxx/` | 单个 Stub 的目录，包含开发交付（`result.md`）、审核记录（`stub-review.md`），以及按需创建的跨 Stub 交接（`handoff.md`）与问题记录（`findings/`） |
| `review.md` | 所有 Stub 通过后的整份 Plan 验收结论（跨 Stub 问题附 `findings/`） |
| `evidence/` | 按需存放通过验收的最终关键证据 |

</details>

### 复用判断与工作方法

<sub>以爻成卦</sub>

**principle** 提供判断标准，**workbook** 定义工作方法；同一条原则可跨领域复用，工作步骤与交接由各自领域的 workbook 约定：

- **规则按需落盘**：`/to-plan` 制定计划时，会把所选 workbook 里的条件规则（调度、执行、审核规则槽）直接展开写进 `summary.md`，后续执行与独立审核照着 Plan 走即可。
- **静态门禁落地**：写代码时可用 [`program-guard-setup`](skills/program-guard-setup/SKILL.md) 将可自动校验的编程原则落成编译器、Linter 与架构依赖检查，而不只停在口头约束。
- **源码耦合审计**：想核查架构真实耦合度时，可显式调用 [`axiomatic-audit`](skills/axiomatic-audit/SKILL.md) 基于 MIT 公理设计直查源码显式依赖与隐式变更耦合，生成可视化矩阵报告。

## Core Skill

Skill 定义 Agent 的行为。

| 要做的事 | Core Skill |
| --- | --- |
| **接入项目，配置门禁与加载依据** | [`toolkit-steward`](skills/toolkit-steward/SKILL.md) · [`program-guard-setup`](skills/program-guard-setup/SKILL.md) · [`workbook`](skills/workbook/SKILL.md) · [`principles`](skills/principles/SKILL.md) |
| **调查现状，推敲设计** | [`how`](skills/how/SKILL.md) · [`why`](skills/why/SKILL.md) · [`effect`](skills/effect/SKILL.md) · [`axiomatic-audit`](skills/axiomatic-audit/SKILL.md) · [`architect`](skills/architect/SKILL.md) |
| **规划工作，执行与审核交付** | [`to-plan`](skills/to-plan/SKILL.md) · [`execute-plan`](skills/execute-plan/SKILL.md) |
| **维护文档、原则与决策** | [`doc-polish`](skills/doc-polish/SKILL.md) · [`principle-maintenance`](skills/principle-maintenance/SKILL.md) · [`decision-maintenance`](skills/decision-maintenance/SKILL.md) |

## 官方扩展

- **[game](extensions/game/README.md)** 为游戏项目提供玩法设计、美术与 UI 规范，以及配套的 workbook 和 principle。
- **[toolkit-maintenance](extensions/toolkit-maintenance/README.md)** 为开发和维护工具包提供扩展开发与结构合规工作方法（`maintenance-extension`），以及覆盖维护治理、扩展边界、知识、workbook、Skill 与工具链的原则体系。

官方扩展按项目启用。项目快照固定所用的扩展资料，后续可用 `harness-install` 预览并同步。安装步骤见[目标安装与项目接入](docs/getting-started.md#目标安装与项目接入)。

## 深入了解

- **设计与决策**　[体系架构](skills/toolkit-steward/references/architecture.md) · [项目决策索引](docs/knowledge/decisions/index.md)
- **能力与工具**　[Skill 与 CLI 索引](skills/toolkit-steward/references/capabilities.md)
- **开发与维护**　[开发环境](docs/getting-started.md) · [参与开发](CONTRIBUTING.md) · [维护与发布](docs/maintenance.md) · [工具包更新记录](CHANGELOG.md) · [CLI 更新记录](docs/cli-changelog.md)
- **许可**　[MIT License](LICENSE) · [第三方内容声明](THIRD_PARTY_NOTICES.md)

本页采用默认的 Agile 模式。工具包也提供 [Flow 模式](skills/to-plan/references/flow/guide.md)。
