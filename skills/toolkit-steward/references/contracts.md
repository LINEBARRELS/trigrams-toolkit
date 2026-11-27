# 数据归属与交接契约

| 数据 | 唯一事实来源 | 工具职责 |
| --- | --- | --- |
| 工作要求 | `agile`：`summary.md`（含 YAML `plan-type: agile`、`status` 与 Stub 清单）；`flow`：`summary.md`、`tasks/T01/task.md` | `flow` 模式由 `plan-toolkit` 检查目录结构与依赖关系；`agile` 模式不经由 `plan-toolkit` |
| 调度快照与当前状态 | `agile`：`summary.md` YAML 头 `status`；`flow`：Plan 目录的 `plan.json`（定义从文稿编译） | `agile` 模式由调度者直接维护 `status`；`flow` 模式由 `plan-toolkit` 同步快照、计算可执行任务并更新状态 |
| 实际交付与审核 | `agile`：Plan 目录下按 Stub 划分的 `Sxx/`（`result.md`、按需 `handoff.md`、`stub-review.md`、按需 `findings/Rxx.md`）与根级 `review.md`（及按需 `findings/Rxx.md`）；`flow`：Task 目录及明确引用的源码和证据 | 普通文件，由对应执行与审核入口消费 |
| 架构身份与关系 | `.project-state/state.json` 及文稿头维护的身份与归属元数据 | `project-state` 统一维护文稿头与索引，提供定位与关系查询 |
| workbook 与 principle | `WORKBOOK.md`、`PRINCIPLE.md` 的正文和头信息 | `handbook` 发现、加载、校验与原则入库 |
| 资源声明与安装归属 | 扩展 `assets/extension.json`、`docs/resources.json`、`.agents/harness.json`、`skills-lock.json` | `harness-install` 负责快照装配与受管文件基线保护；Skill 目录由 Vercel skills 管理 |
| 迁移清单 | 项目根 `migration/` | 按初始化流程调查、经用户确认与明确开工后执行并更新进度 |
| 退役项目资料 | `docs/archives/` 下的分类目录 | 按已确认清单移动原件，保留来源对应关系 |
| 旧运行状态归档 | `.harness-archive/<批次>/` | `harness-install archive` 原样移动指定的项目内相对路径 |

## 核心契约规则

- **架构与计划状态**：
  - Registry 保存 Module、Feature 和 Spec 的架构关系。
  - `agile` 模式的 Plan 直接以 `summary.md` 统筹工作目标、验收标准、规则约束并定义 Stub，调度者直接更新 `status` 并按以 Stub 为基本单元推进开发与独立审核。
  - `flow` 模式的 Plan 使用 `plan-toolkit` 管理下属 Task，执行调度和状态切换。
- **公共 CLI 工具路径参数**：公共 CLI 工具参数中的项目内相对路径以项目根目录为基准。在 Git 工作树中则使用工作树的目录。
- **安装与基线保护**：扩展快照装配遵循“先预览、后应用”，通过文件基线保护受管文件与用户本地修改；相同安装请求支持幂等重放。各工具的详细子命令与参数约束通过 `<工具> --help` 查询。
