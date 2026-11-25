# 能力地图与工作流分工

## Skill 职责

| 入口 | 职责 |
| --- | --- |
| `toolkit-steward` | 解答工具包架构、契约与选用依据，诊断环境与项目状态，引导项目接入与扩展管理 |
| `workbook` / `principles` | 按任务目标和范围检索并加载适用的 workbook 或 principle |
| `to-plan` | 将已确定目标编写为可执行 Plan（默认 `agile` 模式） |
| `execute-plan` | 组织 Plan 的开发与独立审核交接、成果整合 |
| `execute-task` | 在 `flow` 模式下完成单个 Task 实现与必要验证 |
| `delivery-review` | 在 `flow` 模式下核对实际交付物与验收标准，形成审核结论 |
| `architect` | 维护宏观架构（ARD）、Module / Feature 边界与 Implementation Spec |
| `doc-polish` | 中文技术文档标准语言规范与润色检查 |
| `how` / `why` / `effect` | 调查当前实现机制与历史设计决策理由；在用户显式触发时评估变更影响范围 |
| `principle-maintenance` / `decision-maintenance` | 提炼与入库项目 principle 草稿；在用户显式触发时提炼、修订与演进项目决策记录 |
| `answer-me-with-html` / `smell-check` | 外部必需全局依赖，分别负责可视化架构报告与代码坏味道审计。应用项目装配时补齐缺项 |

## 公共工具

四个公共 CLI 使用统一版本。用 `<工具> --help` 查询子命令、参数与输入输出结构。业务命令在目标项目根执行。

| 公共工具 | 职责 |
| --- | --- |
| `plan-toolkit` | 面向 `flow` 模式编译 Plan 快照、检查任务依赖、查询可执行任务并维护 Plan 与 Task 状态 |
| `project-state` | 登记和查询项目内 Module、Feature、Artifact 的身份与关系 |
| `handbook` | 发现、加载和校验核心、扩展与项目自建的 workbook 及 principle，并将已审定原则草稿入库 |
| `harness-install` | 预览并装配项目扩展资源与宿主 adapter，补齐全局 Skill，保护受管文件并归档指定项目内路径 |

## 工作流分工与扩展协作

| 工作目标 | 推荐入口 | 核心交付 |
| --- | --- | --- |
| 单步调查或专项工作 | 对应基础或领域 Skill | 事实结论、代码／文稿产物或专项判断 |
| 编写或修订计划 | `to-plan` | `agile`：`summary.md`（含 Stub 清单）与规划自检；`flow`：`summary.md`、各 `task.md` 与拓扑校验 |
| 组织 Plan 全流程执行 | `execute-plan` | 开发与独立审核调度、成果整合、状态推进与总体结论 |
| 执行 `flow` 单个开发任务 | `execute-task` 或领域 Skill | 实际交付产物、验证记录与未决事项 |
| 独立核对 `flow` 交付质量 | `delivery-review` | 审核结论、缺陷证据与整改要求 |
| 项目配置、接入、扩展管理与迁移准备 | `toolkit-steward` → `core:workbook:project-setup` | `.agents/harness.json`、扩展快照、目录骨架、项目核心文档与按需迁移清单 |

`core` 提供跨领域通用能力；领域扩展（如 `game`、`toolkit-maintenance`）补充领域专属 Skill、workbook、principle 与可选成果类型；平台 adapter 为 Codex、Claude Code 和 Pi Web 提供角色子代理入口。
