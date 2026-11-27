---
name: 编程功能开发与修复
description: 在已有正式设计下实现功能、修复缺陷或重构程序；先判定开发工作规模，遵循先框架后逻辑的纪律，按规模划定 Stub 与审核阶段，验证实际行为及消费者。
resourceId: core:workbook:programming-development
includes:
- core:principle:workflow/define-stubs-by-verifiable-delivery-boundaries
- core:principle:programming-workflow/define-contracts-before-implementation
---

# 编程功能开发与修复

## 适用与输入

明确开发目标、验收标准、执行边界、项目现状及关键依据。关键资料缺失或功能前置依赖未确定时及时反馈设计问题。

## 必要工作流程

规划阶段先依据代码结构影响判定本次开发工作规模，作为后续工序切分与规则选用的统一依据：

| 工作规模 | 判定标准 | 推进方式 |
| --- | --- | --- |
| 局部规模 | 小型缺陷修复、局部重构，或在既有模块框架与契约内完成的常规实现 | Stub 在单轮内完成实现与一次综合审核 |
| 架构规模 | 涉及新模块或子系统搭建、跨模块公共契约变更、复杂接口、数据转换边界或扩展流程定义 | Stub 按“框架搭建 → 架构审核 → 逻辑装填 → 功能审核”两阶段推进 |

<schedule-rule>
按本次工作类型确定推进方向与验收重点（向执行者派发工作时可按需随附作为增强指导）：

| 工作 | 方法与验收重点 |
| --- | --- |
| 功能 | 沿入口、状态与消费者核对设计，复用既有能力；明确新增代码功能逻辑、边界处理和兼容要求，再实现可观察结果 |
| 修复 | 用最小代表场景复现期望与实际的差异，定位原因；修复后重验原场景、相关边界与消费者 |
| 重构 | 明确应保留的行为、公开契约及当前验证依据；按独立可验证范围改结构，持续核对行为与兼容性 |
</schedule-rule>

<exec-rule>
执行编程工作时，遵循先确立框架契约、再填充具体逻辑与算法的流程，完成后重验目标行为及受影响消费者，并清除代码中已失效的待办注释。

按当前工作内容按需加载 principle：
- **架构与抽象设计：** 必读 `programming-design-architecture` scope 下的全部原则。按设计问题选读：抽象、状态建模、模块边界和目录组织分别查 `programming-design-abstraction`、`programming-design-state`、`programming-design-module` 和 `programming-design-repo`。
- **源码溯源标识：** 除单文件微小修补外，加载 `core:principle:programming-workflow/trace-source-declarations-to-plan-stubs` 维护 `@plan-stub` 注释。
- **编程语言规范：** 按涉及编程语言从对应语言 scope（如 `programming-csharp`、`programming-python`、`programming-typescript-javascript`）加载对应 principle。

模块内有沉淀价值的局部经验时，可在模块所在目录用 `KNOWLEDGE.md` 记录简短、内聚的非强制建议；内容应聚焦模块内部，不外链或耦合模块外代码。
</exec-rule>

<exec-rule if="当前工作处于架构规模">
Stub 开发分为框架搭建与逻辑装填两阶段：框架搭建阶段仅交付代码骨架、类型声明、公共契约与 TODO 注释，不提前混入业务逻辑实现；待架构审核通过后，再于逻辑装填阶段补全具体实现。两阶段边界参考如下：

| 交付对象 | 框架搭建阶段确定的内容 | 逻辑装填阶段完成的内容 |
| --- | --- | --- |
| 服务或模块接口 | 职责、公开签名、输入输出与失败语义 | 业务逻辑、边界处理与消费者调用行为 |
| 数据格式与转换边界 | 字段、类型、约束及解析或转换入口 | 解析、校验、转换与真实数据处理 |
| 扩展点或处理流程 | 扩展接口、生命周期、调用顺序与依赖 | 调度、具体处理与组合行为 |
</exec-rule>

## 工序切分与交接

按可独立验证的行为与契约范围划定 Stub。处于架构规模时，按框架搭建与逻辑装填之间的公共契约界定 Stub，单个 Stub 可覆盖共同服务于该契约的类、函数与数据声明。

<schedule-rule if="当前工作处于架构规模">
每个 Stub 均按“框架搭建 → 架构审核 → 逻辑装填 → 功能审核”两阶段推进：
1. Stub 框架搭建完成后，先派发独立架构审核；
2. 架构审核通过后，再推进该 Stub 的逻辑装填与独立功能审核；
3. 需消费完整行为的下游工作应等待上游 Stub 装填阶段审核通过。
</schedule-rule>

## 产出与验收

<review-rule if="当前工作处于架构规模">
**架构审核（Stub 框架搭建阶段）：** 加载 `programming-review` 全部 principle 及当前编程语言 principle，审查代码框架质量，核对是否提前混入业务逻辑，并通过编译、导入或类型检查确认框架无报错、实际可用。本阶段通过仅证明结构与契约可用，不替代完整功能验收。

**功能审核（Stub 逻辑装填阶段）：** 加载当前编程语言 principle，审查代码质量与完成度；核对设计契约、边界处理与运行证据，确认实际修改、运行结果与证据一致，列明未运行范围与原因。
</review-rule>
<review-rule else>
**综合审核：** 加载 `programming-review` scope 全部 principle 及当前编程语言 principle，审查代码质量与完成度；核对设计契约、边界处理与运行证据，确认实际修改、运行结果与证据一致，列明未运行范围与原因。
</review-rule>
