---
name: to-plan
description: 基于当前工作目标和相关文档，选择 workbook、principle，创建或修订 Plan（工作计划）并完成规划检查；Use only when explicitly specified。
metadata:
  harness-toolkit-type: workflow
---

# to-plan

## 模式分流

选择一种模式并读取对应总文档：

- **Agile 模式（默认）**：读取并执行[Agile 模式规划指引](references/agile/guide.md)。
- **Flow 模式（按需）**：仅用户显式指定时使用。读取并执行[Flow 模式规划指引](references/flow/guide.md)。

## 跨模式共性规则

1. **方法与原则准备**：规划前通过 workbook skill 选择适配的工作方式文档，使用 principles skill 读取所选的 workbook 文档的 `includes` 中记录的原则。正式依据缺少关键公共契约时，明确缺项，继续不依赖缺项的规划。
2. **文稿精炼与依据定位**：动笔编辑文档前使用 doc-polish skill。已有正式依据可通过路径与章节引用定位，不在 Plan 中大段复抄既有决策、设计正文或通用运行规则。
3. **以正式设计为依据**：Plan 仅以已确认的正式设计为准；`docs/research/` 属于未定型的探索草稿，不应在 Plan 中参考或引用。
4. **保留历史审计证据**：已完成的 Plan 与交付记录属于审计证据，现行代码演进与引用重构不应逆向修改历史 Plan 正文与任务数据。
