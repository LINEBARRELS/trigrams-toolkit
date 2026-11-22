# 更新记录

版本号以 `toolkit.json` 与 `pyproject.toml` 为准，四个公共 CLI 的 `--version` 统一来自 Python 包元数据。

## 0.3.1

- 从 [skills/architect/SKILL.md](skills/architect/SKILL.md) 抽离架构可视化报告公共约束至 [report-guide.md](skills/architect/references/report-guide.md)，并由 [ARD 报告指引](skills/architect/references/ard-report.md) 与 [Spec 报告指引](skills/architect/references/implementation-spec-report.md) 统一引用。
- 修正 [architect](skills/architect/SKILL.md)、[exploration-experiments.md](skills/architect/references/exploration-experiments.md)、[report-guide.md](skills/architect/references/report-guide.md) 与 [programming-development](skills/workbook/workbooks/programming-development/WORKBOOK.md) 中把 principle `scope` 误作单条原则或残留旧聚合表述的写法，明确按 `scope` 筛选与加载原则。
- 明确 [extension-setup-toolkit-maintenance](extensions/toolkit-maintenance/skills/extension-setup-toolkit-maintenance/SKILL.md) 中按工作对象加载的是维护 `workbook`，并将 [Handbook 协议](src/trigrams_toolkit/resources/handbook/PROTOCOL.md) 中的 `programming-design` 示例同步为 `programming-design-architecture`。

## 0.3.0

- 将架构可视化报告的全局外部依赖从 `archify` 替换为 `answer-me-with-html`（`QingYunA/answer-me-with-html`），同步更新 `harness-install` 的全局依赖声明、装配协议、第三方声明及项目接入文档。
- 重构 `architect` 的可视化汇报流程与 [ARD 报告指引](skills/architect/references/ard-report.md)、[Spec 报告指引](skills/architect/references/implementation-spec-report.md)：采用 `tree`、`flow`、`sequence`、`class`、`state`、`api`、`er` 等原生组件展示架构与执行流程，支持 `+`/`-`/`~` 变更对比与 `ask` 审阅决策卡片，并禁止借用源码实现补充设计事实。
- 新增显式触发的工作流 Skill `program-guard-setup`，为 TypeScript/JavaScript、C#/.NET 与 Python 提供按原则映射编译器、Linter 与架构检查的工具链指引，并在 `verify_toolkit.py` 中校验其原则引用。
- 更新 `keep-code-within-scale-limits` 规模检查表述及首页 `README.md` 引导说明。

## 0.2.0

- `handbook`、`plan-toolkit` 与 `project-state` 从当前目录向上查找最近的 `.agents/harness.json`，在项目子目录中也能定位项目资源、Plan 与登记状态。查找范围受 `.git` 和 `.tmp` 边界限制。扩展装配命令 `harness-install` 以当前目录为准。
- 统一上述三个 CLI 的项目内相对路径解析规则，并补充项目根发现、边界与子目录调用的回归测试。
- 按 `project-setup` 基线整理仓库的 `AGENTS.md`，预留 Plan 与复盘目录。
- 更新 GitHub 首页，加入水墨横幅、快速接入说明与 core Skill 导航。项目展示名称统一为 Trigrams toolkit。

## 0.1.1

- 新增 `.github/workflows/release.yml` 与 `python tasks.py check-release`，在推送 `v*` 标签后通过 PyPI Trusted Publishing（OIDC）自动执行版本核对、构建、跨平台验收并发布发行包；完善 `pyproject.toml` `[project.urls]` 与 `docs/pypi-readme.md` 公开链接。
- 将 `core:workbook:initialize` 重构为 `core:workbook:project-setup`，按“基础配置与资源核对 → 目录骨架搭建 → 项目级核心文档维护”三大核心底座、可选扩展管理（工作 4）与显式触发的存量迁移清单（工作 5）分层；从 `toolkit-steward` 抽离扩展管理，统一按路径读取扩展 setup。
- 将 `extension-setup-game` 与 `extension-setup-toolkit-maintenance` 规范为四段正交结构，并关闭模型自动调用（`disable-model-invocation: true` 与 `agents/openai.yaml`）。
- 同步更新 `plan-toolkit`、`project-state` 重建提示语及协议文档中的 `project-setup` 引用；新增根 [README.md](README.md)，并在公开文档中补全正式 GitHub／PyPI 来源与精简安装命令。

## 0.1.0

- 统一发布 Python CLI 包 `trigrams-toolkit`，提供 `plan-toolkit`、`project-state`、`handbook` 与 `harness-install` 四个标准入口，并随包交付协议 schema、核心类型与宿主 adapter 模板。
- 四个 CLI 的帮助（`-h`／`--help`）与版本（`-v`／`--version`）可在任意目录查询；业务命令均在目标项目根目录执行。
- `plan-toolkit` 通过 `inspect`、`mark`、`block`、`cancel` 查询和维护计划与任务状态，Task 目录保存工作要求与交付证据。
- `project-state` 将 Module、Feature、Artifact 身份与额外关系保存在项目根的 `.project-state/state.json`，提供公共实体视图查询：`locate` 返回单实体，`related` 返回一跳 `items` 与 `relations`，`list` 返回基础视图。
- `handbook` 按正文头发现并加载全局 core、项目扩展快照与项目自建的 workbook 与 principle，支持多 ID 批量加载、`validate` 校验与 `import-principle` 原则入库。
- `harness-install` 预览并装配项目扩展快照（`.agents/extensions/<extension>/`）与宿主 adapter，保存 SHA-256 基线并在首次装配、增补或同步时补齐全局 `archify` 与 `smell-check`；提供 `archive PATH...` 归档明确的项目内相对路径。
- core Skill（`skills/`）与领域扩展（`extensions/game/`、`extensions/toolkit-maintenance/`）通过 Vercel skills 分发；`core:workbook:initialize` 随模板提供 `.gitignore`、`.ignore`、`.rgignore` 与基础项目文档结构。
- 支持 Windows 与 Linux 本机路径，并提供面向 PR 与发布候选的跨平台 CI 校验与隔离包验收流程。
