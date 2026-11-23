---
name: effect
description: 仅在用户显式调用时，评估设计、workbook 或 principle 变更对成果、使用方和在途工作的影响。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# effect

只读评估变更如何波及现有成果、实际使用方与在途工作，识别真实风险与待验证前提。

- **取证入口**：从变更前后内容与已知使用方出发，结合源码、文稿及 `docs/implementation-specs/`、`docs/knowledge/decisions/`、`docs/knowledge/retrospectives/` 排查实际依赖。按需只读调用 `project-state`、`plan-toolkit` 或 `handbook`。
- **关键约束**：
  - 除显式差异外，排查隐含语义变化与 Registry 之外的实际使用方，不局限于已登记关系。
  - 区分已确认影响、已排除风险与待验证前提；需要补查当前机制或历史依据时，分别转 `how`、`why`。
  - 涉及在途工作时，仅指出受影响的未完成 Plan 目录及其在途 Stub（`agile` 模式）或 Task（`flow` 模式）；不修改已完成历史记录，工具失败或快照异常时**不补写或同步**，记为取证缺口。
- **执行方式**：影响面较广时，可派发只读 subagent 探索并整理结论。
- **输出要求**：先给出条理清晰的结论与最小验证建议，再附上必要的文件、符号或目录链接。
