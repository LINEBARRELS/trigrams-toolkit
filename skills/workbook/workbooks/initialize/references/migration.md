# 旧项目迁移

本说明维护旧项目的调查、清单与成果重建方法。执行与等待用户确认的时机遵循[主 workbook](../WORKBOOK.md#必要工作流程)。

## 目标信息调查

调查项目规则、工程结构、正式文稿、工具归属、已有身份、在途工作和写入者。从入口与正式目录定位，沿引用和历史补查，核对本地修改及现状与目标的差异。

| 目标成果 | 搜寻线索 | 价值判断与生成方式 |
| --- | --- | --- |
| PRODUCT、DESIGN、DEVTECH、ARD | 项目介绍、正式需求、视觉规范、架构总纲与工程结构 | 提取仍有效的范围、方向、工程约束与职责边界，采用 `core:workbook:document-production` 整理唯一正文 |
| Implementation Spec | 模块设计、接口与状态设计、技术方案及对应代码和测试 | 原件归档到 `docs/archives/coding-specs/`；结合实现核验，按 `architect` 模板整合为标准 Spec |
| decisions | ADR、方案对比、旧开发记录、PR 讨论与关键提交说明 | 按原主题与来源提炼仍影响选择的问题、前提、备选、选择与理由，写入 `docs/knowledge/decisions/`（保留原历史标签）；必要时用 `why` 补查 |
| retrospectives | 故障、调试、返工、发布记录及真实 Git 区间 | 提炼有证据的关键变化、处置与结果，写入 `docs/knowledge/retrospectives/`；有 Git 区间时采用 `core:workbook:git-history` |
| 项目 workbooks | 维护说明、Runbook、重复任务步骤与脚本说明 | 比对 core 与所选扩展，只提炼项目方法增量；采用 `core:workbook:meta` 编写并演练 `docs/workbooks/<主题>/` |
| 项目 principles | 旧项目规则、反复出现的取舍、评审准则与复盘经验 | 提炼跨任务适用且条件明确的判断准则；用 `principle-maintenance` 在 `docs/research/principle-drafts/` 形成草稿，经用户审定后用 `handbook import-principle` 入库 |
| 模块 KNOWLEDGE | 局部维护提示、代码旁经验与旧交接说明 | 核实后提炼模块内非强制建议，写入对应 `KNOWLEDGE.md` |
| 后续 Plan / Task | 旧 Plan、TODO、路线图、Issue、未完成分支与已落盘成果 | 筛选仍有效目标、可用成果与验收缺口，明确本次接管或后续安排，按实际内容重新核定状态 |

同一来源可为多个目标提供证据，原件只保留一份。无高价值信息的类别标明未发现或不适用。研究与外部资料保留来源和未确定项；实现与设计冲突时写入清单待确认。现有有效规则在迁移期间继续保留，principle 候选草稿待审不阻塞独立工作。

## 迁移清单与确认

结合调查结果与用户已给出的意见，在项目根编写 `migration/checklist.md`（多次迁移时按主题分文件，编辑文稿前使用 `doc-polish`）。用可勾选条目记录工作与完成情况，相关资料可按目录归并，关键差异单列。清单包含：

| 内容 | 必要信息 |
| --- | --- |
| 目标结构 | 目标项目根、平台与扩展、目标目录、根 `AGENTS.md` 合并方案、保留的工程结构 |
| 来源与发现 | 具体路径、章节或外部条目，发现的信息及迁移价值 |
| 处置与产物 | 保留、归档、提炼或重编方式，原件去向、新成果路径及验收 |
| 身份与配置 | 已核实 ID、归属、延续或新建身份的理由、登记库及活动正式文稿的位置 |
| 工作接管 | 原执行者、写入位置、已落盘成果、未完目标、停工及接管安排 |
| 冲突与验证 | 规则冲突、本地修改、已知失败、环境前提和待确认问题 |

开始执行后，按[目录与 AGENTS.md 装配](project-docs.md#目录与-agentsmd-装配)启用新根 `AGENTS.md`，逐项落实清单中的来源、处置与产物要求。

## 保留已有登记库

项目根的 `.project-state/state.json` 符合现行格式时，沿用其中的实体与关系。若项目曾自定义登记库位置或在 Git 工作树间共享登记库，先根据旧映射找到要沿用的登记库，再按确认清单将其置入每个目标项目根的 `.project-state/state.json`。在各自根目录核对正文定位。活动正文迁移后，按原 Artifact ID 更新登记。

## 归档与成果重建

归档前确认相关写入者已停工；无法确认时保留运行位置并交接阻碍。按清单将退役项目资料直接移入对应分类目录，保持正文不变并保留来源对应关系；待替换的旧运行状态按[安装说明](installation.md#旧运行状态归档)用 `harness-install archive` 移走。

| 原件 | 分类目录 |
| --- | --- |
| 被新标准 Spec 接替的正式代码设计 | `docs/archives/coding-specs/` |
| 旧入口、类 Plan 与开发过程记录 | `docs/archives/development-records/` |
| 已确认退役的项目工具 | `docs/archives/tools/` |
| 有保留价值的旧中间数据 | `docs/archives/intermediate-data/` |

只创建实际使用的分类目录；领域资料遵循扩展说明。

Project State 在项目根的 `docs/`、`plans/` 和已登记的 `locatorHint` 查找正文，默认扫描跳过 `docs/archives/`。归档后核对已有 `locatorHint` 仍指向活动正文。若定位失效，按原 ID 重新登记活动正文。核对 Spec 路径、成果类型与归属后，在项目根重建缺失的登记。

1. 运行 `project-state register module` 与 `project-state register feature` 登记架构节点，将真实 ID 回填至 ARD。
2. 运行 `project-state register artifact` 按成果类型（如 `core:architecture-spec` 或扩展领域类型）与完整归属登记活动 Spec，必要时通过 `project-state relate` 登记成果关系。
3. 用 `project-state locate <真实 Artifact ID>` 确认活动正文可正常定位。

同一成果延续时保持原 ID，合并、拆分或重编为新成果时分配新 ID。归档原件保留原文件头，新 Registry 只登记当前活动成果。后续开发引用新成果时使用已登记的真实 ID。

## 验证与交付

核对清单中的来源、归档及新成果对应关系，确认旧原件可查、活动正文唯一且身份可定位。按[主 workbook](../WORKBOOK.md#产出与验收)完成安装、资源与状态校验，将根 `AGENTS.md` 收敛为实际结构，交付接管结果、待审草稿及未运行范围。
