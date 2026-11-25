# Agile 模式调度指引

依据当前 Plan 的 `summary.md` 完成工作，不回查 `workbook`，不调用 `plan-toolkit` 及 Flow 专用 Skill（`execute-task`、`delivery-review`）。

- **规则分工**：主 Agent 遵循 `<schedule-rule>`，开发 subagent 遵循 `<exec-rule>`，审核 subagent 遵循 `<review-rule>`。
- **状态维护**：`summary.md` YAML 头的 `status`（`pending`、`doing`、`blocked`、`done`）仅由主 Agent 维护。

## 执行调度流程

### 1. 启动与断点恢复

核对项目根、Plan 目录及既有 `Sxx-result.md`、`review.md`。

- `status` 为 `pending` 或需从 `blocked` 恢复时，更新为 `doing`。
- 断点恢复时，依据现有 `Sxx-result.md` 与 `review.md` 识别已完成的交付与审核节点，跳过已最终 `pass` 的部分，从中断点续跑。

### 2. 按 Plan 调度开发与审核

默认以 `Stub` 为调度单元，按依赖顺序推进（无依赖且无共享文件竞争时可并行），每个 Stub 经开发交付与独立审核闭环；若 `summary.md` 的 `<schedule-rule>` 定义了附加调度方式和阶段划分，优先遵守 `<schedule-rule>`。

1. **派发开发**：派发独立开发 subagent，告知当前 `summary.md` 路径和本次负责的 Stub，要求其遵守[开发约束文档](dev-constraints.md)。
   1. 开发 agent 汇报因外部缺项受阻时，将 `status` 更新为 `blocked` 并汇报缺项内容并停止工作。
2. **派发审核**：开发交付后，派发独立审核 subagent，告知当前 `summary.md` 路径、本次待核验内容以及开发 agent 汇报的交接产物，要求其遵守[审核约束文档](review-constraints.md)。
3. **审核结论**：
   - **`pass`**：确认产物就绪，推进后续调度。
   - **`rework`**：携带 `open` 问题编号要求开发 agent 返工，完成后复验。
   - **`inconclusive`**：优先指定开发 agent 按 `rework` 处理；明确因外部依据或环境依赖缺失而无法推进时，将 `status` 更新为 `blocked` 并汇报待裁决项。

### 3. Plan 总体终验与收尾

全部必要 Stub 达到最终 `pass` 后，派发独立审核 subagent 执行 Plan 总体终验。基于 `summary.md` 与全部 `Sxx-result.md`，核实整个 Plan 的目标实现、总体验收标准、跨 Stub 一致性（如有）及遗留项，遵守[审核约束文档](review-constraints.md)，审核结论分为：

- **`pass`**：将 Plan 的 `status` 更新为 `done`，完成交付。
- **`rework`**：定位缺陷所属 Stub，进行返工与复验；涉及整体方案偏差时，暂停调度并汇报问题所在。
- **`inconclusive`**：将 `status` 更新为 `blocked` 并汇报待裁决项。
