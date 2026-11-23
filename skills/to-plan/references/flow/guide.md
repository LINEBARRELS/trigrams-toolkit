# Flow 模式规划指引

Flow 模式适用于多模块并行依赖、需跨会话强状态追踪与拓扑校验的复杂任务：通过 `summary.md` 与 `tasks/Txx/task.md` 声明依赖与 Stub 交接，并由 `plan-toolkit` 编译快照和校验拓扑。

## 编写与拆分

按所选 `workbook` 的目标、工序与验收要求，依照[文件格式](format.md)编写 `summary.md`（YAML 头声明 `plan-type: flow`）与各 `tasks/Txx/task.md`。`summary.md` 统筹目标、范围、正式依据、Task 拓扑、Stub 详情与总体验收；新增契约与实现细节交由对应 Task 交付。

Task 记录本次工作特有的目标、输入、边界与验收标准，使执行者凭 Task、关联 Stub 与精确引用即可接手。将适用 principle 分发至对应 Task 的“相关 principle”章节，按条件引用专业 `workbook` 章节。未受正式依据或真实依赖约束的实现路径由执行者选择。

围绕核心工作划定 Stub：遵循所选 `workbook` 的工序与交接要求；没有明确要求时，结合工作目标、成果结构和现状判断。在 Flow 模式下，若某 Stub 需按安装与装填分阶段交接，由不同 Task 分别声明 `installs` 与 `fills` 完成。按真实依赖切分 Task，共享产物存在竞争时用 `dependsOn` 或明确顺序消除竞争。

Task 产出的正式成果需要由调度者登记，或需调用特定业务工具时，写明必要命令、参数来源与返回值处理。

## 校验与审核

完成文稿后，按[定义与状态](format.md#定义与状态)运行 `plan-toolkit validate <Plan目录> --sync` 并处理校验结果。同步成功后，按[验证编排审核](test-review.md)核对交接、文稿精炼度、Spec 输入与验证。

## 修订与交付

修订进行中的 Plan 前核对实际进展，保留已有产物和有效历史结论；改变已完成工作时，用后续 Task 承接修复，并说明哪些结论需要重验。

交付 Plan 目录、校验与审核结果、规划期发现的工作区状态和未解决缺项。
