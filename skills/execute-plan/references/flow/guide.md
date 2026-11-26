# Flow 模式调度指引

Flow 模式适用于含 `tasks/Txx/task.md` 与 `plan.json` 的重型编排 Plan。读取 `summary.md`、Task 定义及 `plan-toolkit inspect <Plan目录>` 的依赖与状态；缺少快照或定义过期时，先交回规划同步。

主 Agent 运行 `plan-toolkit` CLI 流转状态；开发与审核工作应分别派发给独立的 subagent，按当前宿主环境灵活分派，不强行绑定预设角色名。

## 执行调度流程

### 1. 初始化调度

核对当前文件与状态。如果 Plan 处于 `pending` 或需整体恢复，主 Agent 运行 `plan-toolkit mark <Plan目录> doing`。

### 2. Task 就绪计算与循环派发

主 Agent 运行 `plan-toolkit get-task <Plan目录>` 获取当前就绪 Task 列表，按依赖拓扑逐项调度：

1. **就绪检查**：
   - 若存在就绪 Task：选取目标 Task 进入派发。存在文件或契约竞争时按顺序派发。
   - 若无就绪 Task：检查在途任务。若所有必要 Task 均已 `done`，进入[第 3 节 Plan 终验](#3-plan-终验与收尾)；若仍有在途 Task 则等待；若无在途且仍有未完成 Task，运行 `plan-toolkit block <Plan目录> --reason <阻塞原因>` 并报告。

2. **执行开发**：
   - 派发前主 Agent 运行 `plan-toolkit mark <Plan目录> <Task编号> doing`。
   - 派发独立开发 subagent，传递 Task 目录、关联 Stub 阶段要求、工作目录、负责范围与交付位置，要求其遵守[开发约束文档](dev-constraints.md)。
   - 接收开发交付结果：
     - **正常交付**：取得产物路径与验证证据，进入审核环节。
     - **执行受阻**：主 Agent 运行 `plan-toolkit block <Plan目录> <Task编号> --reason <具体阻因与继续位置>`。
     - **任务撤销**：主 Agent 运行 `plan-toolkit cancel <Plan目录> <Task编号> --reason <撤销原因>`。关键 Task 撤销后交回规划同步。

3. **派发审核**：
   - 开发交付完成后，主 Agent 派发独立审核 subagent，传递 Task 目录、关联 Stub 阶段要求、实际产物位置与验证证据，要求其遵守[审核约束文档](review-constraints.md)。
   - 接收审核结论并由主 Agent 流转状态：
     - **`pass`**：确认产物就绪，运行 `plan-toolkit mark <Plan目录> <Task编号> done`。
     - **`rework`**：主 Agent 运行 `plan-toolkit mark <Plan目录> <Task编号> rework`。
     - **`inconclusive`**：若缺项证据可补充，主 Agent 运行 `plan-toolkit mark <Plan目录> <Task编号> rework` 重新派发开发补证；若外部环境缺失无法裁决，运行 `plan-toolkit block <Plan目录> <Task编号> --reason <缺项与受影响范围>`。

4. **推进下一步**：
   状态变更后，重新运行 `plan-toolkit get-task <Plan目录>` 获取下一组候选，重复上述步骤。

### 3. Plan 终验与收尾

当全部必要 Task 均达到 `done` 状态后，主 Agent 组织全局终验：

1. **派发总体审核**：
   主 Agent 派发独立审核 subagent，传递 `summary.md`、总体交付目标、总体验收判据、所有 Task 产物与验证证据，要求其遵守[审核约束文档](review-constraints.md)。
2. **终验结论流转**：
   - **`pass`**：主 Agent 运行 `plan-toolkit mark <Plan目录> done`，完成 Plan 交付。
   - **`rework`**：核对缺陷所在 Task，主 Agent 将受影响的 Task 运行 `plan-toolkit mark <Plan目录> <Task编号> rework`，返回第 2 节重新调度；若涉及架构设计偏差，暂停调度交由规划修订。
   - **`inconclusive`**：主 Agent 确认缺少依据的范围，运行 `plan-toolkit block <Plan目录> --reason <终验未决项>` 并向用户说明待裁决问题。

每次 CLI 命令调用后核对退出码；报错或状态变更被拒绝时停止派发并排查真实状态。
