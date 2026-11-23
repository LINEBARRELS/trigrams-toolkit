---
name: to-plan
description: 基于当前任务需求，选择 workbook、principle 与 Plan 模式（默认 agile 单文档模式，复杂多阶段编排可选 flow 模式），创建或修订 Plan 并完成规划检查。
metadata:
  harness-toolkit-type: workflow
---

# to-plan

## 模式分流

根据任务复杂度与用户要求选择一种模式并读取对应总文档：

- **Agile 模式（默认）**：日常与中小型开发任务使用单文档 Plan，不拆分 Task，不使用 `plan-toolkit`。读取并执行[Agile 模式规划指引](references/agile/guide.md)。
- **Flow 模式（按需）**：用户显式指定 `flow`，或任务具备复杂多模块并发依赖、需跨多会话强状态追踪与拓扑校验时使用。读取并执行[Flow 模式规划指引](references/flow/guide.md)。

## 跨模式共性规则

1. **方法与原则准备**：规划前通过 `workbook` 选择适配的工作方法，结合其 `includes` 与条件指引通过 `principles` 筛选适用原则。正式依据缺少行为、公共契约或验收条件时，明确缺项，继续不依赖缺项的规划。
2. **文稿精炼与依据定位**：动笔编辑文档前使用 `doc-polish`。已有正式依据通过路径与章节引用定位，不在 Plan 中大段复抄既有决策、协议正文或跨 Skill 通用运行规则。规划期的瞬时工作区状态留归会话交付汇报。
3. **禁止引用研究草稿**：严禁在 Plan 或 Task 中引用或提及 `docs/research/` 中的文档，其为不稳定的研究探索，工作仅以明确定稿的正式设计为准。
4. **历史审计不可篡改**：已完成的 Plan、Task 与交付记录属于审计证据，现行代码演进与引用重构不得逆向修改历史 Plan 正文与任务数据。
5. **写入边界与交付汇报**：本入口的写入止于目标 Plan 目录及对应模式的状态同步，不新增或更新项目决策记录。规划期出现值得沉淀的设计取舍或原则冲突裁决时，在交付汇报中单列供用户定夺（需归档决策时由用户显式调用 `decision-maintenance`）。
