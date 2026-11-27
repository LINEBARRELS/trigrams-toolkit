# Agile 模式调度指引

依据当前 Plan 的 `summary.md` 完成工作。

- **规则分工**：主 Agent 遵循 `<schedule-rule>`，开发 subagent 遵循 `<exec-rule>`，审核 subagent 遵循 `<review-rule>`。
- **状态维护**：`summary.md` YAML 头的 `status`（`pending`、`doing`、`blocked`、`done`）仅由主 Agent 维护。

## 目录与文件布局

```text
docs/plans/<label>/
  summary.md              # Plan 唯一正文（含 YAML 状态头与全部 Stub 定义）
  review.md               # Plan 总体终验结论与问题索引
  findings/               # 按需：仅当 Plan 总体终验提出跨 Stub 问题时创建
    R01.md
  evidence/               # 按需仅存放通过验收的最终关键证据
  S01/                    # 执行期开工时按需创建
    result.md             # 开发维护：产物清单与验证依据
    handoff.md            # 开发按需维护：交接与遗留（无特殊交接时不创建）
    stub-review.md        # 审核维护：各轮结论、验证摘要与问题索引
    findings/             # 审核按需维护：每条 Rxx 独立文档（无问题时不创建）
      R01.md
```

## 执行调度流程

### 1. 启动与断点恢复

核对 Plan 目录及既有 `Sxx/stub-review.md`、`Sxx/result.md`、`review.md`。

- `status` 为 `pending` 或需从 `blocked` 恢复时，更新为 `doing`。
- 断点恢复时，优先依据各 `Sxx/stub-review.md` 与根级 `review.md` 识别已完成的交付与审核节点，跳过已最终 `pass` 的部分，从中断点续跑。

### 2. 按 Plan 调度开发与审核

默认以 `Stub` 为调度单元，按依赖顺序推进（无依赖且无共享文件竞争时可并行），每个 Stub 经开发交付与独立审核闭环；若 `summary.md` 的 `<schedule-rule>` 定义了附加调度方式和阶段划分，优先遵守 `<schedule-rule>`。

1. **派发开发**：派发独立开发 subagent，告知当前 `summary.md` 路径、本次负责的 Stub 目录（`<Plan目录>/<StubID>/`）及所需上游 `handoff.md`（如有），要求其遵守[开发约束文档](dev-constraints.md)。
   1. 开发 agent 汇报因外部缺项受阻时，将 `status` 更新为 `blocked` 并汇报缺项内容并停止工作。
2. **派发审核**：开发交付后，派发独立审核 subagent，告知当前 `summary.md` 路径、本次待核验的 Stub 以及开发 agent 汇报的交接产物，要求其遵守[审核约束文档](review-constraints.md)。
3. **审核结论**：
   - **`pass`**：确认产物就绪，推进后续调度。
   - **`rework`**：从 `Sxx/stub-review.md` 的问题索引读取 `open` 条目，将对应的 `Sxx/findings/Rxx.md` 路径派发给开发 agent 返工（多个正交问题且无共享文件竞争时可拆分并行返工），完成后复验。
   - **`inconclusive`**：优先指定开发 agent 携带对应 `findings/Rxx.md` 按 `rework` 处理；明确因外部依据或环境依赖缺失而无法推进时，将 `status` 更新为 `blocked` 并汇报待裁决项。

### 3. Plan 总体终验与收尾

全部必要 Stub 达到最终 `pass` 后，派发独立审核 subagent 执行 Plan 总体终验，命令其：
- 基于 `summary.md` 与各 `Sxx/`（优先核对 `stub-review.md`、`result.md` 及按需存在的 `handoff.md`），核实整个 Plan 的目标实现、总体验收标准、跨 Stub 一致性（如有）及遗留项，遵守[审核约束文档](review-constraints.md)

根据返回的审核结论：
  - **`pass`**：将 Plan 的 `status` 更新为 `done`，完成交付。
  - **`rework`**：定位缺陷所属 Stub 或按根级 `findings/Rxx.md` 派发返工与复验；涉及整体方案偏差时，暂停调度并汇报问题所在。
  - **`inconclusive`**：将 `status` 更新为 `blocked` 并汇报待裁决项。
