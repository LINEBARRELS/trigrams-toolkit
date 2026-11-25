---
name: execute-plan
description: 调度、完成一个 Plan 的开发流程循环，派发独立执行与审核 subagent，组织交付、整合与 Plan 状态维护。
metadata:
  harness-toolkit-type: workflow
---

# execute-plan

## 模式识别与分流

读取目标 Plan 目录内的 `summary.md`，按其 YAML 头 `plan-type` 字段进行分流：

- **`plan-type: agile`**：读取并执行[Agile 模式调度指引](references/agile/guide.md)。
- **`plan-type: flow` 或未声明 `plan-type`（legacy 兼容）**：读取并执行[Flow 模式调度指引](references/flow/guide.md)。

## plan 调度通用规则

1. **严格职责隔离**：主 Agent 专职负责流程调度、维护 Plan 状态与派发独立 subagent；**严禁**直接编写或修改业务代码、执行业务实现脚本或自行生成验收证据。
2. **开发与审核独立**：开发与审核工作应分别派发给独立的 subagent。缺少独立 subagent 能力时，暂停执行并向用户报告。
3. **历史审计不可篡改**：严禁修改非当前 Plan 或已完成 Plan 的历史报告与审核记录。
