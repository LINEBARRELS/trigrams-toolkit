# 数据归属与交接契约

| 数据 | 唯一事实来源 | 工具职责 |
| --- | --- | --- |
| 工作要求 | `summary.md`、`tasks/T01/task.md` | `plan-toolkit` 检查目录结构与依赖关系 |
| 调度快照与当前状态 | Plan 目录的 `plan.json`（定义从文稿编译） | `plan-toolkit` 同步快照、计算可执行任务并更新状态 |
| 实际交付与审核 | Task 目录及明确引用的源码和证据 | 普通文件，由对应执行与审核入口消费 |
| 架构身份与关系 | `.project-state/state.json` 及文稿头维护的身份与归属元数据 | `project-state` 统一维护文稿头与索引，提供定位与关系查询 |
| workbook 与 principle | `WORKBOOK.md`、`PRINCIPLE.md` 的正文和头信息 | `handbook` 发现、加载、校验与原则入库 |
| 资源声明与安装归属 | 扩展 `assets/extension.json`、`docs/resources.json`、`.agents/harness.json`、`skills-lock.json` | `harness-install` 负责快照装配与受管文件基线保护；Skill 目录由 Vercel skills 管理 |
| 迁移清单 | 项目根 `migration/` | 按初始化流程调查、经用户确认与明确开工后执行并更新进度 |
| 退役项目资料 | `docs/archives/` 下的分类目录 | 按已确认清单移动原件，保留来源对应关系 |
| 旧运行状态归档 | `.harness-archive/<批次>/` | `harness-install archive` 原样移动指定的项目内相对路径 |

## 核心契约规则

- **架构与计划状态**：Task 的 `specs` 引用真实文稿 ID。Registry 保存 Module、Feature 和 Spec 的架构关系；Plan 状态写入使用文件锁与原子替换。`validate --sync` 从文稿生成结构快照并保留任务进展；Stub 先 `installed` 后 `filled`，`uses` 等待 `installed`，完整行为依赖通过 `dependsOn` 表达。
- **项目根**。四个公共 CLI 从进程当前目录读取项目。命令参数中的项目内相对路径以项目根为基准。每个 Git 工作树使用自己的 Registry、Plan 和装配快照。
- **安装与基线保护**：扩展快照与平台 adapter 装配遵循“先预览、后应用”，通过文件基线保护受管文件与用户本地修改；相同安装请求支持幂等重放。各工具的详细子命令与参数约束通过 `<工具> --help` 查询。
