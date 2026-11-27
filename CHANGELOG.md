# 更新记录

本页记录工具包版本，版本号以 `toolkit.json` 为准。CLI 版本以 `pyproject.toml` 为准，见 [CLI 更新记录](docs/cli-changelog.md)。

## 0.6.1

- `architect` 的 Implementation Spec 用目标语言的精简声明定义核心类型和公开签名，并用文字补充数据所有权、不变量和失败语义。模板新增常驻的生命周期与驱动机制小节，报告指引同步更新。[架构设计 Skill](skills/architect/SKILL.md) · [Implementation Spec 模板](skills/architect/references/templates/implementation-spec.temp.md) · [报告指引](skills/architect/references/implementation-spec-report.md)
- `principle-maintenance` 在起草新原则前核对已有 scope，优先复用匹配的 scope，并检查候选名称是否重名。[原则维护 Skill](skills/principle-maintenance/SKILL.md)
- 编程开发 workbook 明确按任务涉及的语言加载对应 scope 下的 principle。[编程开发 workbook](skills/workbook/workbooks/programming-development/WORKBOOK.md)

## 0.6.0

- 新增 `axiomatic-audit`。显式调用后，审查源码中的显式依赖和隐式变更耦合，并用设计矩阵呈现证据与结论。[审计 Skill](skills/axiomatic-audit/SKILL.md)
- `execute-plan` 统一承担 Agile 和 Flow 的执行入口。原 `execute-task` 与 `delivery-review` 的约束并入 Flow 指南，由调度者派发开发和审核子代理。[执行 Skill](skills/execute-plan/SKILL.md)
- Agile Plan 在 `summary.md` 中展开适用的调度、执行与审核规则。每个 Stub 的交付和审核记录归入对应目录。[Agile 规划指南](skills/to-plan/references/agile/guide.md)
- 新增防止测试反推领域模型的审核原则，补充 C#、Python 和 TypeScript 的类型与分派原则，并同步 `program-guard-setup` 的静态检查映射。[编程门禁 Skill](skills/program-guard-setup/SKILL.md)
- 项目装配以 `agent` 指定宿主，并沿用已有扩展配置。使用新版装配指南前，先升级 CLI 至 `0.6.0`。[CLI 更新记录](docs/cli-changelog.md#060)

## 0.5.4

- 工具包与 CLI 独立发布。工具包用 `vX.Y.Z` 标签，CLI 用 `vcli-X.Y.Z` 标签触发 PyPI 发布。[维护与发布](docs/maintenance.md#ci-与发布)

## 0.5.3

- 明确 `doc-polish` 在编辑技术类或产品类文档前加载语言规范。美术与文本创作保留原有表达。[文档润色 Skill](skills/doc-polish/SKILL.md)

## 0.5.2

- 明确 `architect` 的 Implementation Spec 承载 Module 与 Feature 的详细程序设计。模板集中定义模块边界、公开契约和核心状态，并按模块形态选用运行机制与可靠性章节。[架构设计 Skill](skills/architect/SKILL.md) · [Implementation Spec 模板](skills/architect/references/templates/implementation-spec.temp.md)
- Implementation Spec 的可视化报告将独立功能流和复杂子流程分别成图。[报告指引](skills/architect/references/implementation-spec-report.md)

## 0.5.1

- 明确 `architect` 的可视化汇报交接。主 Agent 提供设计文档、引用和报告指引的路径，子代理独立读取指引并生成 ARD 或 Implementation Spec 的 HTML 报告。[架构设计 Skill](skills/architect/SKILL.md)
- README 增加首份 Plan 的规划与执行示例，并介绍默认 Agile 模式的交付流程和文件结构。[README](README.md)

## 0.5.0

- `to-plan` 改为显式调用。新建 Plan 默认采用 Agile 模式，Flow 模式需显式指定。Agile Plan 在 `summary.md` 定义可独立验收的 Stub，在 `Sxx-result.md` 记录开发交付和审核，在 `review.md` 记录整体验收。[规划指引](skills/to-plan/SKILL.md) · [Agile 调度指引](skills/execute-plan/references/agile/guide.md)
- `plan-toolkit` 仅处理 Flow Plan。带 `plan-type: agile` 的 Plan 返回 `unsupported_plan`，未知的 `plan-type` 返回 `invalid_plan`。未声明 `plan-type` 的既有 Flow Plan 仍可读取。[Plan 协议](src/trigrams_toolkit/resources/plan/PROTOCOL.md)
- Workbook 可按条件将调度、执行和审核规则写入 Agile Plan。编程开发 workbook 按改动规模选择单轮交付或分阶段审核。[Agile 规划指引](skills/to-plan/references/agile/guide.md) · [编程开发 workbook](skills/workbook/workbooks/programming-development/WORKBOOK.md)
- `toolkit-maintenance` 将 `maintenance-knowledge`、`maintenance-skill`、`maintenance-tooling` 和 `maintenance-workbook` 合入 `maintenance-extension`，并将维护原则整理为 6 个 scope。同时移除 `core:workbook:document-production`。升级时，已接入维护扩展的项目可同步扩展快照，并更新项目中指向已移除资源的引用。[维护扩展](extensions/toolkit-maintenance/README.md) · [项目接入](docs/getting-started.md)
- `architect` 要求 ARD 至少定义一个带 `（Arch）` 标记的框架模块。框架模块负责工程底座，业务模块负责领域行为，登记时保留模块原名。[架构设计 Skill](skills/architect/SKILL.md)
- CI 将 4 组平台检查汇总为 `PR checks`。发版 PR 校验源码并验收发行包，发布标签工作流构建并跨平台验收实际上传 PyPI 的发行包。[维护与发布](docs/maintenance.md)

## 0.3.4

- 明确 `architect` 编写 DEVTECH、ARD 或 Implementation Spec 时可参阅 `docs/research/` 中的研究内容。正式文档中仍禁止添加指向这些研究文档的链接。[architect](skills/architect/SKILL.md)

## 0.3.3

- 明确正式设计、计划交付与 `docs/research/` 研究草稿的边界：在 [architect](skills/architect/SKILL.md)、[to-plan](skills/to-plan/SKILL.md)、`execute-task` 与 [project-setup `AGENTS.md` 模板](skills/workbook/workbooks/project-setup/assets/templates/AGENTS.md) 中禁止在正式设计文档、Plan 与 Task 中引用研究草稿，执行阶段统一以正式设计为准。
- 建立 `dev`（日常集成）+ `main`（正式发版）双分支工作流与本地保护钩子（`.githooks/pre-commit`、`.githooks/pre-push`），并在 [参与维护](CONTRIBUTING.md)、[开发与接入](docs/getting-started.md) 与 [维护与发布](docs/maintenance.md) 中补充分支策略、合并方式与 GitHub Rulesets 配置说明。
- 在 [tasks.py](tasks.py) 新增 `bump`（原子对齐 `pyproject.toml`、`toolkit.json` 与各资源清单版本）和 `setup-hooks` 子命令。
- 更新 [ci.yml](.github/workflows/ci.yml) 与 [release.yml](.github/workflows/release.yml)：面向 `main` 的 Release PR 自动执行打包与隔离验收，每日定时巡检跟踪 `origin/dev`，并在发布标签构建前校验其属于 `origin/main` 历史。

## 0.3.2

- 精简 [how](skills/how/SKILL.md)、[why](skills/why/SKILL.md) 与 [effect](skills/effect/SKILL.md) 为聚焦取证入口、关键约束、子代理探索与输出要求的紧凑说明，去除通用常识与 Git 检索引导。
- 将 [effect](skills/effect/SKILL.md) 设为仅用户显式调用（`disable-model-invocation: true` 与 `skills/effect/agents/openai.yaml`），移除 [decision-maintenance](skills/decision-maintenance/SKILL.md) 与 [principle-maintenance](skills/principle-maintenance/SKILL.md) 对 `effect` 的自动引用，并同步更新 [capabilities.md](skills/toolkit-steward/references/capabilities.md) 说明。
- 简化 [architect](skills/architect/SKILL.md) 的探索引导表述，移除已不再单独维护的 `exploration-experiments.md` 指引，并同步修正 `0.3.1` 记录中的失效路径链接。
- 移除 `.rgignore` 与 `skills/workbook/workbooks/project-setup/assets/templates/.rgignore` 中的注释行。

## 0.3.1

- 从 [skills/architect/SKILL.md](skills/architect/SKILL.md) 抽离架构可视化报告公共约束至 [report-guide.md](skills/architect/references/report-guide.md)，并由 [ARD 报告指引](skills/architect/references/ard-report.md) 与 [Spec 报告指引](skills/architect/references/implementation-spec-report.md) 统一引用。
- 修正 [architect](skills/architect/SKILL.md)、`skills/architect/references/exploration-experiments.md`、[report-guide.md](skills/architect/references/report-guide.md) 与 [programming-development](skills/workbook/workbooks/programming-development/WORKBOOK.md) 中把 principle `scope` 误作单条原则或残留旧聚合表述的写法，明确按 `scope` 筛选与加载原则。
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
