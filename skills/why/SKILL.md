---
name: why
description: 按问题追溯历史决策与关键变更，解释设计选择、约束和取舍代价。
metadata:
  harness-toolkit-type: workflow
---

# why

从历史记录而非当前代码倒推原因：只读追溯当时的目标、约束与取舍，并评估如今是否仍适用。

- **取证入口**：优先阅读用户指定材料，按需查阅 `docs/knowledge/decisions/`、`docs/knowledge/retrospectives/`、`docs/plans/`；核对现行设计时参考 `docs/implementation-specs/`。涉及查询登记身份、关系或 Plan 进度时，只读调用 `project-state`、`plan-toolkit`。
- **关键约束**：
  - 严格区分记录依据、合理推断与未知项，不看代码强行合理化；记录冲突无法消解时保留竞争解释。
  - 查询失败或快照缺失、过期时，**不补写或同步**，如实记为取证缺口。
- **执行方式**：任务复杂或线索分散时，可派发只读 subagent 检索并整理结论。
- **输出要求**：先给出条理清晰的结论与当前适用性判断，再附上必要的文件、记录或目录链接。
