---
name: to-plan
description: 基于当前任务需求，选择 workbook、principle，收集所需信息，创建或修订 Plan 及所属 Task，并完成计划检查。
metadata:
  harness-toolkit-type: workflow
---

# to-plan

## 准备规划

基于当前用户意图与任务目标，通过 `workbook` 选择适配的工作方法，结合其 `includes` 与条件指引通过 `principles` 筛选适用 principle。正式依据缺少行为、公共契约或验收条件时，明确缺项，继续不依赖缺项的规划。

## 编写与拆分

动笔编辑文档前使用 `doc-polish`。按所选 `workbook` 的目标、流程与验收要求，依照[文件格式](references/format.md)编写 `summary.md` 和 Task。summary 统筹目标、范围、正式依据、Task 拓扑、Stub 详情与总体验收；已有依据通过路径和章节引用定位，新增契约与实现细节交由对应 Task 交付。

Task 记录本次工作特有的目标、输入、边界与验收标准，使执行者凭 Task、关联 Stub 与精确引用即可接手。将适用 principle 分发至对应 Task 的“相关 principle”章节，按条件引用专业 `workbook` 章节。未受正式依据或真实依赖约束的实现路径由执行者选择。

围绕核心工作考虑 Stub 的划定：遵循所选 `workbook` 的要求；没有明确要求时，结合工作目标、成果结构和现状判断。Stub 定义工作产出边界、安装与装填要求，由不同 Task 分阶段完成。按真实依赖切分 Task，共享产物存在竞争时用依赖或明确顺序消除竞争。

Task 产出的正式成果需要由调度者登记，或需调用特定业务工具时，写明必要命令、参数来源与返回值处理。跨 Skill 的运行与状态规则由对应 Skill 承担；规划期的瞬时工作区状态留归会话交付汇报。

严禁在 Plan 或 Task 中引用或提及 `docs/research/` 中的文档，其为不稳定的研究探索，工作仅以明确定稿的正式设计为准。

## 校验与审核

完成文稿后，按[定义与状态](references/format.md#定义与状态)运行 `plan-toolkit validate <Plan目录> --sync` 并处理校验结果。同步成功后，按[验证编排审核](references/test-review.md)核对交接、文稿精炼度、Spec 输入与验证。

## 修订与交付

已完成的 Plan 与 Task 属于交付审计记录，现行代码演进与引用重构不得逆向修改历史 Plan 正文与任务数据。修订前核对实际进展，保留已有产物和有效历史结论；改变已完成工作时，用后续 Task 承接修复，并说明哪些结论需要重验。

本入口的写入止于目标 Plan 目录及快照同步，不新增或更新项目决策记录。规划期出现值得保留的设计取舍或原则冲突裁决时，在交付汇报中单列供用户定夺（需归档决策时由用户显式调用 `decision-maintenance`）。交付 Plan 目录、检查结果、规划期发现的工作区状态和未解决缺项。
