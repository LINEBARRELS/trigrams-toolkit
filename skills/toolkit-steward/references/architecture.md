# Trigrams 体系架构与核心设计

本文件维护 Trigrams toolkit 的宏观职责、知识组织与分发边界。

## 1. 体系目标与职责关系

工具包采用统一的项目工作协议：Skill 负责行为，workbook 定义工作方法，principle 指导判断，正式成果（Artifact）保存项目依据与交付物，Plan 组织目标、Task 与依赖。

| 组成 | 职责 |
| --- | --- |
| **Skill** | 调查、规划、执行、审核、解释和维护；读取依据并调用工具 |
| **workbook** | 定义适用条件、输入、工作方法、任务切分、交接与验收 |
| **principle** | 提供特定工作范围内普适的判断标准 |
| **Artifact** | 保存正式设计与交付物；正文单点维护，身份与关系进入登记库 |
| **Plan / Task** | Plan 统筹目标，Task 定义工作、依据、产物与验收 |
| **项目知识** | 保存项目 principle、规划决策、关键变更和模块建议，按用途维护 |
| **公共工具** | 维护身份、定位、当前状态、资料检索与安装归属 |
| **extensions / adapters** | 扩展补充领域能力，平台适配器随 CLI 包提供宿主角色入口 |

简单问答和单步工作直接使用对应能力。多阶段工作、跨角色交接或持续追踪通过 Plan 组织。跨 Plan 生效的判断标准归 principle，单次工作要求归 Plan 或 Task。

## 2. Skill 封装与跨组件协作

每个 Skill 封装自身正文、私有资料（`references/`）和私有脚本（`scripts/`）。

- **跨 Skill 协作**：使用宿主标准入口，明确说明使用条件、输入与所需结果；调用方严禁直接读取另一 Skill 的私有文件。
- **渐进式加载（Progressive Disclosure）**：principle 和 workbook 通过对应 Skill 按范围或稳定 ID 按需加载，资源内部可使用相对路径；指定资源或能力缺失时，返回缺项与影响范围。
- **上下文隔离模式**：复杂知识查询与多维建议按对应 Skill 的隔离要求执行。`how`、`why`、`effect` 推荐使用子代理，也可在主线程完成；`toolkit-steward` 的咨询分流与主线程执行边界由其 [Skill 入口](../SKILL.md)规定，主线程只加载当前问题所需资料。

## 3. principle 与 workbook 机制

内置 principle 采用 `principles/<scope>/<principle>/PRINCIPLE.md` 两级目录：一级目录为完整 scope，二级英文小写连字符目录为原则名称，由来源与目录派生 `<source>:principle:<scope>/<principle>`。principle 头信息只接受 `description`，单条保存完整判断、条件与必要例外，加载时只返回自身。项目原则草稿保存于 `docs/research/principle-drafts/`，不参与正式索引；经用户审定批准后通过 `handbook import-principle` 入库，清单声明由 CLI 自动维护。

Agent 按任务相关性从索引中选择原则；固定流程的必读原则由对应 workbook 的 `includes` 声明。workbook 可递归包含 workbook 与 principle，保留目录前缀分类与显式身份。编程设计与语言规则归内置 principle，中文技术文档标准由 `doc-polish` 单点维护。

- **来源发现**：`handbook` 独立发现目标 agent 全局 `principles`、`workbook` Skill 中的核心资料、项目已装配的 `.agents/extensions/<extension>/` 扩展快照资料，以及项目 `docs/resources.json` 声明的自建资料。
- **冲突裁决**：principle 按正文适用条件使用；不同来源出现矛盾时明确条件、影响与待裁决问题，不通过目录顺序推导优先级。

## 4. 项目知识分层管理

当前正式设计维护唯一正文；迁移中被新标准成果接替的旧设计按已确认清单归档到 `docs/archives/`。项目入口展示当前文档与规则，历史演进与影响分析由 `why`、`effect` 承担。

| 内容 | 用途与维护责任 |
| --- | --- |
| **正式成果** | 作为当前工作的直接依据，按对应流程修订 |
| **项目 principle** | 按范围生效；由 `principle-maintenance` 维护 |
| **模块经验** | 模块内简短、内聚的非强制指导与建议（`KNOWLEDGE.md`）；按当前问题读取 |
| **decisions** | 方案选择、约束与取舍理由；迁移时按清单提炼历史决策，用户显式触发 `decision-maintenance` 时提炼与演进 |
| **retrospectives** | 关键变化、已记录背景与结果；由对应 workbook 整理，Git 历史是其中一种证据来源 |
| **research / references** | 保存研究草稿和外部资料，不自动成为正式约束 |
| **Plan 与过程证据** | 在授权的规划、执行和审核范围内记录 |

## 5. 包层次与分发边界

| 层次 | 职责与分发方式 |
| --- | --- |
| **core Skill** | 通用行为 Skill 及随 `principles`、`workbook` 携带的核心资料；通过 Vercel skills 全局安装到目标 agent |
| **公共工具** | 四个统一 Python CLI（`plan-toolkit`、`project-state`、`handbook`、`harness-install`）；通过包管理器安装，契约、核心类型与 adapter 模板随包交付 |
| **外部必需 Skill** | `answer-me-with-html` 与 `smell-check`。`harness-install install apply` 在首次装配、增补或同步时通过 Vercel skills 补齐目标 `agent` 的全局安装 |
| **项目扩展与快照** | 扩展 Skill（含 `extension-setup-<extension>`）通过 Vercel skills 安装到项目；`harness-install` 将 `assets/` 装配为 `.agents/extensions/<extension>/` 快照并复制宿主 adapter，`.agents/harness.json` 记录版本与文件基线 |
| **项目自有内容** | 正式成果、Plan、知识、自建资料（`docs/resources.json`）与本地配置 |
| **adapters** | 宿主 subagent 入口直接调用 core Skill，维护角色模型与权限配置 |

全局扩展来源不自动启用项目扩展。上游扩展 Skill 更新后，由 `harness-install` 显式预览并同步项目快照；显式同步前项目继续读取既有快照。
