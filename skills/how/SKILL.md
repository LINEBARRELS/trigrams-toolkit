---
name: how
description: 调查当前设计结构、工作过程、职责分工和在途 Plan 状态。
metadata:
  harness-toolkit-type: workflow
---

# how

只读调查当前实现、职责边界与在途状态，说清系统实际如何运转。

- **取证入口**：优先阅读用户指定材料与源码；按需查阅 `DEVTECH.md`、`docs/ARD.md`、`docs/implementation-specs/`。查询登记身份与关系时只读调用 `project-state`；查询在途 Plan 进度时按 `summary.md` 的 `plan-type` 区分：`agile` 模式直接只读查看 `summary.md`（YAML 头 `status` 与 Stub 清单）及同级平铺的 `Sxx-result.md`／`review.md`，`flow` 模式（含未声明 `plan-type` 的历史 Plan）只读调用 `plan-toolkit`。
- **关键约束**：
  - 区分设计意图与当前实际行为，存在分歧直接指出。
  - 查询失败或快照缺失、过期时，**不补写或同步**，如实记为取证缺口。
- **执行方式**：任务复杂或范围较广时，可派发只读 subagent 探索并整理结论。
- **输出要求**：先给出条理清晰的结论，再附上必要的文件、符号或目录链接。
