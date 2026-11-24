# Agile 模式调度指引

Agile 模式直接以 `summary.md` 为唯一工作依据推进交付：不回查 `workbook`，不调用 `plan-toolkit` CLI，不使用绑定了 `execute-task`／`delivery-review` Skill 的专用角色 adapter，而是由主 Agent 智能派发**通用独立 subagent** 并告知其遵守预设约束文档。

## 执行调度流程

### 1. 初始化与状态恢复

核对目标项目根、Plan 目录、工作区及目录内既有的平铺结果文件（`Sxx-result.md`、`review.md`）。

- 若 `summary.md` YAML 头的 `status` 为 `pending` 或需从 `blocked` 恢复，主 Agent 将其更新为 `doing`。
- 断点恢复时，核对各 `Sxx-result.md` 中的审核记录，跳过最终阶段已审核 `pass` 的 Stub。

### 2. 按 Stub 推进开发与审核

依据 `summary.md` 的 `## 附加调度规则` 与 `## Stub 清单`（范围、前置依赖与共享文件竞争约束），按序或分批推进待完成 Stub：

1. **派发开发（通用独立 subagent）**：
   - 派发通用独立 subagent（不指示其调用 `execute-task` Skill），在派发指令中清晰交付：
     - 目标项目根、Plan 目录与当前负责的 Stub 定义（如 `S01`）及本轮阶段范围（若 `## 附加调度规则` 对该 Stub 声明了多阶段推进，明确当前推进到哪一阶段）；
     - `summary.md` 中相关的需求目标、正式依据、验收标准与用户补充约束；
     - 本轮必读的基线 `principle` ID 列表（来自 `summary.md` 的 `## 正式依据` 及对应 Stub 的补充 principle）；
     - 本 Stub 的平铺交付结果路径（`<Plan目录>/<StubID>-result.md`）；
     - 明确要求先阅读并遵守[开发约束文档](dev-constraints.md)。
   - 若为返工，一并传递对应 `Sxx-result.md` 中状态为 `open` 的问题编号及要求。
   - 接收开发交付结果：正常完成时进入审核环节；若因外部缺项受阻，停止推进该分支，将 `summary.md` 头 `status` 更新为 `blocked` 并向用户报告具体阻因与继续条件。

2. **派发独立审核（通用独立 subagent）**：
   - **默认节奏**：单个 Stub 开发完成后派发一次独立审核。
   - **多阶段节奏**：若 `summary.md` 的 `## 附加调度规则` 对该 Stub 声明了多阶段推进与审核（例如先架构安装审核、再逻辑装填审核），则在每个声明的阶段完成后分别派发独立审核；前阶段审核 `pass` 后再派发下一阶段开发。
   - 派发独立的通用审核 subagent（不指示其调用 `delivery-review` Skill），在派发指令中清晰交付：
     - 目标项目根、当前 Stub 要求、当前审核阶段与对应验收标准；
     - 实际产物路径与对应 `<Plan目录>/<StubID>-result.md`；
     - 该阶段必读的审核与领域 `principle` ID（来自 `summary.md` 的 `## 验收标准`、`## 附加调度规则` 及对应 Stub）；
     - 明确要求先阅读并遵守[审核约束文档](review-constraints.md)。

3. **处理审核结论与正式登记**：
   - **`pass`**：确认产物就绪。若 `summary.md` 的 `## 附加调度规则` 在该 Stub 或当前阶段 `pass` 后声明了 `project-state` 等正式成果或关系登记，由主 Agent 按要求执行登记命令并核对退出码（登记失败时暂不视为完成）；随后推进下一阶段或下一 Stub。
   - **`rework`**：依据审核记录中未解决的问题清单，重新派发开发 subagent 返工，完成后再派发独立审核复验。
   - **`inconclusive`**：若缺项证据可由开发补充，按 `rework` 重新派发开发补证；若外部依据或验证环境缺失无法裁决，将 `summary.md` 头 `status` 更新为 `blocked` 并向用户说明待裁决项。

### 3. Plan 终验与收尾

当全部必要 Stub 均达到 `pass` 状态后，按 Stub 数量收尾：

- **单 Stub Plan**：唯一 Stub 的最终阶段审核 `pass` 且必要登记完成后，该审核即视同整体验收，直接将 `summary.md` 头 `status` 更新为 `done`，完成交付。
- **多 Stub Plan**：派发一次通用独立审核 subagent，对照 `summary.md` 的总体需求目标、验收标准及全部 `Sxx-result.md` 核验跨 Stub 集成一致性与遗留项，要求其遵守[审核约束文档](review-constraints.md)并将总体终验结论写入 `<Plan目录>/review.md`：
  - **`pass`**：将 `summary.md` 头 `status` 更新为 `done`，完成交付。
  - **`rework`**：定位缺陷所属 Stub，返回第 2 节重新派发开发返工与复验；若涉及整体方案偏差，暂停调度并报告用户修订 Plan。
  - **`inconclusive`**：将 `summary.md` 头 `status` 更新为 `blocked` 并向用户说明未决项。
