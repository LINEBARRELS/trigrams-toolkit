---
name: 编程功能开发与修复
description: 在已有正式设计下实现功能、修复缺陷或重构程序，由 arch Task 安装 Stub 框架，再由 coding Task 装填逻辑与算法，验证实际行为及消费者。
resourceId: core:workbook:programming-development
includes:
- core:principle:programming/define-framework-before-implementation
- core:principle:programming/mark-stubs-and-handoff-notes-in-source
---

# 编程功能开发与修复

## 适用与输入

输入期望行为、当前实现、公共契约、项目验证入口及关键依据。公共行为未确定时反馈设计问题；资料缺口只阻断依赖该信息的部分。

## 必要工作流程

执行前按本次工作阶段与决策点，通过 `handbook list --kind principle` 从对应 scope 选择并 `handbook load` 所需的条件原则：
- **arch 框架设计：** 必读 `programming-design-architecture` 下的全部原则；将 `programming-design-abstraction` 作为关键选读，按最小权威状态与派生计算、状态所有权、组合与继承建模、错误契约等决策点选取；涉及模块边界、仓库结构或实用取舍判断时，从 `programming-design-module`、`programming-design-repo`、`programming-pragmatic` 中按触发情境选取对应原则。
- **arch 验收评审：** 审核者验收 arch Task 产出时，必读 `programming-review` 下的全部原则，排查隐式耦合、不必要耦合与冗余中间层。
- **规模上限核对：** 审查或核对参数量、源文件行数、函数有效行与嵌套深度上限时，加载 `core:principle:programming-scale/keep-code-within-scale-limits`。
- **特定语言规范：** 声明类型与公开签名，或编写、修改、重构特定语言逻辑时，从涉及语言的 scope（`programming-csharp`、`programming-python`、`programming-typescript-javascript`）中选取对应的声明期或实现期原则。

| 工作 | 方法与验收重点 |
| --- | --- |
| 功能 | 沿入口、状态与消费者核对设计，复用既有能力；明确新增行为、失败语义及兼容要求，再实现可观察结果 |
| 修复 | 用最小代表场景复现期望与实际的差异，定位原因；修复后重验原场景、相关边界与消费者 |
| 重构 | 明确应保留的行为、公开契约及当前验证依据；按独立可验证范围改结构，持续核对行为与兼容性 |

按上表确定本次行为范围与验证场景。arch 核对既有框架，补齐类、函数签名、类型、常量、枚举与核心工具定义，按必读原则标记源码并写明装填约束。安装验收通过后，coding 填充逻辑与算法，重验目标行为及受影响消费者。

## Task 切分与交接

每项开发交付均安排 arch 与 coding 两类 Task，并声明 Stub。arch 负责 `installs`，coding 负责 Stub 的 `fills`。arch Task 应配备 `programming-design-architecture` 必读原则、`programming-design-abstraction` 关键选读原则与 `programming-review` 架构验收必读原则，并在验收标准中写明审核者须加载 `programming-review` 原则执行架构审查；涉及其他设计子域或特定语言时，为对应 Task 声明条件原则读取要求。

按可独立验证的行为组织交付，可安排多组 arch 与 coding Task。arch 交付源码框架、契约和安装证据；coding 消费已安装框架并交付完整行为。已有框架由 arch 核对、复用并补齐本次所需定义。依赖完整行为的后续 Task 通过 `dependsOn` 等待 coding 交付。

### Stub 定义与两阶段验收

按 arch 与 coding 之间的框架契约定义 Stub。一个 Stub 可覆盖共同服务于该契约的类、函数和数据声明。常见交接对象如下，按本次需求选用：

| 交接对象 | 安装阶段确定的内容 | 装填阶段完成的内容 |
| --- | --- | --- |
| 服务或模块接口 | 职责、公开签名、输入输出与失败语义 | 业务逻辑、边界处理与消费者调用行为 |
| 数据格式与转换边界 | 字段、类型、约束及解析或转换入口 | 解析、校验、转换与真实数据处理 |
| 扩展点或处理流程 | 扩展接口、生命周期、调用顺序与依赖 | 调度、具体处理与组合行为 |

## 产出与验收

- **安装验收：** 审核者加载 `programming-review` 下的全部原则，严格审查框架设计是否存在隐式变更耦合（如派生状态冗余存储与多真相源同步、隐式全局状态、未声明的调用时序约定）、不必要耦合（如反向依赖、泄漏内部结构、调用方特判参数污染）与无独立变化理由的冗余包装或假扩展点。声明与约定一致，源码标识和交接注释可定位。按承载形式选择编译、导入、类型检查或最小消费者接入，确认下游能按约定引用骨架。安装通过只证明结构与契约可用，完整运行行为由装填验收确认。
- **装填验收：** 待装填行为已实现，并符合安装阶段确定的契约。通过代表性输入、关键边界与消费者调用验证完整行为；涉及组合流程时验证接入后的结果。按必读原则更新交接注释，清除已失效的待办。

核对可观察行为、边界场景与消费者调用，交付实际修改、运行结果与证据。列出未运行范围与原因。

模块内有沉淀价值的局部经验时，可在对应的文件夹内用 `KNOWLEDGE.md` 记录简短、内聚的非强制指导与建议；正文仅限解释本模块，保持解耦。
