# 八卦 Trigrams toolkit

面向软件与游戏工程的跨领域 Agent 工具包，连接项目接入、架构设计、计划调度、任务交付与状态登记。体系由统一 Python CLI 包（[PyPI: `trigrams-toolkit`](https://pypi.org/project/trigrams-toolkit/)）、通过 Vercel skills 分发的 core／扩展 Skill，以及受内容基线保护的项目级扩展快照组成。

- **GitHub 仓库**：https://github.com/LINEBARRELS/trigrams-toolkit
- **PyPI 发行包**：https://pypi.org/project/trigrams-toolkit/
- **运行要求**：Python 3.11+、Node.js（用于 `npx skills`）
- **开源许可**：[MIT License](LICENSE)

## 快速开始

### 1. 安装全局 CLI 与 core Skill

```sh
# 安装四个全局公共 CLI（project-state / plan-toolkit / handbook / harness-install）
uv tool install trigrams-toolkit

# 将 14 个 core Skill 与核心资料全局安装至通用 ~/.agents/skills/ 目录
npx skills add LINEBARRELS/trigrams-toolkit/skills --skill '*' -g
```

> 使用 Claude Code 时如需同步链接至 `~/.claude/skills/`，可在命令末尾附加 `-a claude-code`。

四个公共 CLI 的帮助（`-h`／`--help`）与版本（`-v`／`--version`）可在任意目录查看；业务命令须在目标项目根目录执行。

### 2. 项目首次接入与安装扩展

在目标项目根目录中，如需启用官方扩展（如 `game` 或 `toolkit-maintenance`），先安装对应扩展 Skill（进入项目 `.agents/skills/`；Claude Code 可附加 `-a claude-code`）：

```sh
# 示例：安装 game 扩展 Skill
npx skills add LINEBARRELS/trigrams-toolkit/extensions/game/skills --skill '*'

# 示例：安装 toolkit-maintenance 扩展 Skill
npx skills add LINEBARRELS/trigrams-toolkit/extensions/toolkit-maintenance/skills --skill '*'
```

随后以全局 `toolkit-steward` Skill 为入口，按[项目接入与扩展管理](skills/toolkit-steward/references/project-integration.md)加载 `core:workbook:initialize`，运行 `harness-install` 预览并应用项目快照（`.agents/extensions/<extension>/`）与宿主 adapter；首次应用装配时会自动检查并补齐目标 `agent` 的全局必需依赖 `archify` 与 `smell-check`。

## 组成与能力

| 组成 | 位置 / 入口 | 职责 |
| --- | --- | --- |
| **公共 CLI（4 个）** | [src/trigrams_toolkit/](src/trigrams_toolkit/__init__.py) | `project-state`（架构实体与关系登记）、`plan-toolkit`（计划快照与任务调度）、`handbook`（workbook／principle 检索、校验与入库）、`harness-install`（扩展快照装配、全局依赖补齐与路径归档） |
| **core Skill（14 个）** | [skills/](skills/resources.json) | `toolkit-steward`、`workbook`、`principles`、`to-plan`、`execute-plan`、`execute-task`、`delivery-review`、`architect`、`doc-polish`、`how`、`why`、`effect`、`principle-maintenance`、`decision-maintenance` |
| **game 扩展** | [extensions/game/](extensions/game/README.md) | 玩法设计（`game-designer`）、美术与 UI 规范（`art-designer`）、`extension-setup-game` 及配套玩法／体验／规则／运行证据原则与 workbook |
| **toolkit-maintenance 扩展** | [extensions/toolkit-maintenance/](extensions/toolkit-maintenance/README.md) | 工具包扩展开发、知识库、workbook、工具部署与 Skill 审核规程与原则 |
| **宿主 adapter** | [src/trigrams_toolkit/resources/adapters/](src/trigrams_toolkit/resources/adapters/codex/README.md) | 随 Python 包交付的 Codex、Claude Code 与 Pi Web 角色子代理入口模板 |

## 文档导航

- [开发与接入指南](docs/getting-started.md)：开发环境准备、`tasks.py` 校验／构建／发布入口与三段接入流程。
- [维护与发布说明](docs/maintenance.md)：唯一维护源、定向测试范围与 CI／发布策略。
- [体系架构与核心设计](skills/toolkit-steward/references/architecture.md)：职责分工、知识分层、渐进式加载与分发边界。
- [全局安装与恢复指引](skills/toolkit-steward/references/deployment.md)：全局 CLI、core Skill 与故障诊断。
- [项目决策索引](docs/knowledge/decisions/index.md)：核心架构与工具契约的 ADR 索引。
- [参与维护](CONTRIBUTING.md)：贡献流程、验证要求与本仓狗食 `.gitignore` 约定。
- [更新记录](CHANGELOG.md) · [第三方内容声明](THIRD_PARTY_NOTICES.md)

## 本地开发与验证

```sh
python -m pip install -e '.[dev]'
python tasks.py check            # 资源校验、协议校验与 mypy
python tasks.py test             # 运行 tests/ 与 tests/runtime/ 全部测试
python tasks.py build            # 构建 sdist 与 wheel 至 dist/
python tasks.py verify-package   # 隔离安装并验收 dist/ 发行包
```
