# 存量迁移与归档

本说明对应[主 workbook](../WORKBOOK.md#原子工作目录)的**工作 5（存量迁移与归档清单）**。

工作 5 为**后置可选工作**：默认在基础配置、扩展、目录与核心文档就绪后，按用户意愿启动。先只读调查并输出建议清单，取得用户明确选择后再决定是否执行、执行哪些条目或转为后续 Plan。

## 存量信息调查

从项目既有入口、文档目录与 Git 历史只读排查具有迁移或归档价值的材料，不凭空补全缺失信息：

| 目标类别 | 搜寻线索 | 建议处置方式 |
| --- | --- | --- |
| 核心项目文档 | 旧项目介绍、需求说明、视觉规范、技术总纲 | 提炼仍有效的内容补入 `PRODUCT.md`、`DESIGN.md`、`DEVTECH.md`；架构边界与 `docs/ARD.md` 交由 `architect` 承接 |
| Implementation Spec | 模块设计、接口／状态方案及对应代码 | 原件归档至 `docs/archives/coding-specs/`；结合代码核验后按 `architect` 模板整理 |
| decisions | ADR、方案对比、PR 讨论与关键提交 | 提炼仍影响决策的问题、选择与理由，写入 `docs/knowledge/decisions/`（保留原历史标签） |
| retrospectives | 故障、返工、发布记录及 Git 区间 | 提炼有证据的变更与结果，写入 `docs/knowledge/retrospectives/`（有 Git 区间时可用 `core:workbook:git-history`） |
| 项目 workbooks / principles | 旧 Runbook、维护规范、重复评审准则 | 仅提炼相对 core 与扩展的增量；workbook 用 `core:workbook:meta`，principle 用 `principle-maintenance` 产草稿并经审定后 `handbook import-principle` 入库 |
| 模块 KNOWLEDGE | 代码旁局部经验与旧交接说明 | 核实后提炼非强制建议写入模块内 `KNOWLEDGE.md` |
| 在途 Plan / TODO / 分支 | 旧 Plan、路线图、未完成分支与已落盘产物 | 筛选有效目标与验收缺口，转为后续独立 Plan 承接 |

无高价值信息的类别标明未发现或不适用。研究与外部资料保留来源；实现与旧设计冲突时写入清单待确认。

## 建议清单与确认

结合调查结果在项目根编写 `migration/checklist.md`（按主题拆分时放在 `migration/` 下，编辑前使用 `doc-polish`），用可勾选条目列出：

| 清单内容 | 说明 |
| --- | --- |
| 来源与发现 | 具体路径或条目、发现的有效信息与迁移价值 |
| 建议处置与去向 | 保留、提炼、归档或交由后续 Plan／`architect` 承接，注明原件去向与目标路径 |
| 身份与状态 | 已有 `.project-state/state.json` 或旧 Plan 的留用、归档或重建建议 |
| 风险与待确认项 | 规则冲突、在途写入者、已知失败与待用户拍板事项 |

输出清单后暂停，由用户选择处置方式：

- **仅保留清单**：结束本次工作，后续按需推进。
- **执行部分或全部条目**：仅按用户确认的条目执行归档、提炼与状态重建。
- **转交正式规划**：将大范围重构或架构迁移交由 `to-plan` 建 Plan 追踪。

## 归档与登记库重建（仅在确认执行时）

### 退役资料归档

归档前确认相关写入者已停工。将确认退役的原件移入对应分类目录，保持正文不变并在清单记录对应关系（仅创建实际使用的目录；领域资料遵循对应扩展说明）：

| 原件类型 | 归档目录 |
| --- | --- |
| 被新标准 Spec 接替的旧代码设计 | `docs/archives/coding-specs/` |
| 旧入口、类 Plan 与开发过程记录 | `docs/archives/development-records/` |
| 已确认退役的项目工具 | `docs/archives/tools/` |
| 有保留价值的旧中间数据 | `docs/archives/intermediate-data/` |

### 保留或重建 `.project-state/state.json`

- 现有 `.project-state/state.json` 符合现行格式时直接沿用；自定义路径或共享登记库按确认方案迁回项目根 `.project-state/state.json` 后核对定位。
- 旧登记库格式不兼容或需重建时，先用 `harness-install archive` 移走旧运行状态，再按实际活动正文重建登记：
  1. `project-state register module` / `register feature` 登记架构节点。
  2. `project-state register artifact` 按类型（如 `core:architecture-spec` 或扩展领域类型）登记活动正文，必要时用 `project-state relate` 登记关系。
  3. 同一成果延续时保持原 ID；合并、拆分或重编时分配新 ID。归档原件保留原文件头，登记库只记录活动正文。
- 执行后运行 `project-state validate` 与 `project-state locate <Artifact ID>` 核对活动正文可达，并同步更新 `migration/checklist.md` 完成状态与 `AGENTS.md` 路径。
