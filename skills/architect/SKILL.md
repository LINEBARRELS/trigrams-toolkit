---
name: architect
description: 探索技术设计，或维护 DEVTECH、ARD 与代码实现 Spec。用于宏观架构、Module / Feature 边界、公共契约和技术设计变更。
metadata:
  harness-toolkit-type: workflow
---

# architect

使用 `principles` skill，加载 `programming-design-architecture` scope 下的全部原则。按设计问题选择其他 scope：抽象、状态建模、模块边界和目录组织分别查 `programming-design-abstraction`、`programming-design-state`、`programming-design-module` 和 `programming-design-repo`。涉及类型、属性、常量或公共签名声明时，从对应编程语言的 scope 中选取适用 principle。各种文档的保存路径默认使用 `DEVTECH.md`、`docs/ARD.md`、`docs/implementation-specs/` 和 `docs/research/`。

## 设计与文档

正式文档记录已确定的架构设计；未定方案与设计研讨归入研究目录。动笔编辑文档前使用 `doc-polish`。

- **非正式的设计探索**：当用户的工作目标不涉及维护下面的三种正式文档、仅希望做前期调研时，基于项目现状和设计目标，比较设计候选方案，记录设计研究方案、待裁决问题，保存至 `docs/research/`，基于探索主题创建对应的、可复用专题子文件夹。
- **DEVTECH**：维护技术栈、工程组织、架构层（`Architecture Layer`）清单、宏观职责、依赖方向、所有权与跨模块通用术语。结合应用运行形态，沿外部交互与表现、应用编排、核心业务决策及底层支撑的职责与稳定性差异，垂直切分项目实际所需的架构层。在“应用架构”中列明当前项目的 `Architecture Layer` 划分，界定各层职责边界、单向依赖方向、调用方式及运行环境约束。
- **ARD**：依据 `DEVTECH` 已确立的 `Architecture Layer` 清单，规划并展示当前架构的 `Module → Feature` 结构，使用下方格式。若 `DEVTECH` 未列明当前项目的 `Architecture Layer` 清单或现有层级无法覆盖本次变更时，因缺少稳定的层级划分基准，无法维护 `ARD` 架构树；应先停工、通知用户在 `DEVTECH` 中确立或修订架构层划分。Module、Feature 名称使用 `kebab-case` 格式，职责简述使用用户语言。Feature 按行为职责进行正交划分。
  - **框架模块（`Arch`）**：ARD 应明确定义承载代码工程底座的 “框架模块”，其作为代码工程落地的第一步。框架模块及其内部 Feature 定义最终代码工程的物理与运行形态（如包与工程管理、主循环与启动器、容器与依赖装配、层内公共底座契约...），并决定各架构层内业务模块的具体实现与承载方式（类、包、子工程、链接库等）。全项目至少设置一个框架模块，其内部 Feature 仅列出框架搭建的关键点，不包含具体业务功能。
  - **Spec 检索**：ARD 不列举模块对应的 Spec；运行 `project-state related <Module ID>`，检查退出码为 0 和 `ok: true` 后，读取 `data.items` 中 Artifact 的 `path`。从 Feature 导航共享资料时，先取 `locate <Feature ID>` 的 `data.moduleId` 或 `related <Feature ID>` 返回的 Module，再查询该 Module。
- **Implementation Spec**：每个 Module 的实现设计集中在一份 Spec，承载 ARD 中该 Module 及其 Feature 的详细程序设计，按[模板](references/templates/implementation-spec.temp.md)编写常驻章节并按需启用可选章节。文档仅约束影响跨模块协作、状态不变量与运行正确性的设计决策，不为填满模板虚构章节，编写时遵循以下准则：
  - **自外向内推导**：先从架构层方向与调用场景出发，界定依赖端口与数据、资源所有权。随后依次提炼领域模型与权威状态、锁定对外签名与失败语义，再展开生命周期与驱动机制。
  - **代码声明定契约**：依赖端口、关键的常量、枚举、领域与持久化结构、公开签名及错误类型，应以项目目标语言写成无函数体的精简声明（跨进程协议可用 IDL 或路由契约）。演进既有模块时沿用工程真实符号。不直接对外暴露的内部状态，仅在承载核心状态机、并发边界或持久化格式时声明骨架。函数体控制流与私有辅助结构留给编码阶段实现。
  - **文字仅补动态语义**：代码声明锁定命名、类型、可空性、可变性与调用签名。自然语言只补充代码未能表达的所有权归属、合法值域、状态不变量、前置后置条件及失败影响。代码已声明的字段与参数不再用文字重复罗列。

ARD 节点格式如下；按实际结构重复 Module 与 Feature。框架模块在模块名后紧接 `（Arch）` 标注（登记 `project-state` 时传入的模块名称不含 `（Arch）`）；已登记节点填写真实 ID，尚未登记时省略 ID 括号，登记成功后回填。

```markdown
## <架构层名称>

### <arch-module-name>（Arch）（<真实 Module ID>）

<框架模块职责简述>

- **<feature-name>（<真实 Feature ID>）**：<框架搭建关键点简述>

### <module-name>（<真实 Module ID>）

<业务模块职责简述>

- **<feature-name>（<真实 Feature ID>）**：<Feature 职责简述>
- **<feature-name>（<真实 Feature ID>）**：<Feature 职责简述>
```

技术术语按适用范围单点维护：模块内术语写入对应 Implementation Spec，跨模块共享时上浮至 DEVTECH 并移除局部重复定义，跨顶层概念同步至 AGENTS.md。直接引用上游规则与术语，不维护多处副本。

开发中遇到设计问题时，确认事实与既有授权，交付文档路径、设计结论与待裁决问题；变更已有正式设计时，列明受影响的 Spec、公共契约、消费者及重新验证范围。

## 身份登记与回写

仅在获授权的正式交付时，依次登记本次工作涉及的正式文件与架构实体。

1. **Module**：新建时运行 `project-state register module "<Module 名称>"`，将返回的实体 ID 回填至 ARD 对应节点。已有 Module 改名时带 `--id <已有 Module ID>` 保持身份。
2. **Feature**：新建时运行 `project-state register feature "<Feature 名称>" --module <Module ID>`，将返回的实体 ID 回填至 ARD 对应节点。已有 Feature 改名或调整归属时传入原 `--id` 与目标 `--module`。
3. **Implementation Spec**：运行 `project-state register artifact <Spec 路径> --kind core:architecture-spec --module <Module ID>`，以重复的 `--feature <Feature ID>` 提交本 Spec 覆盖的 Feature 列表。工具自动分配并维护文稿头中的身份与归属，将类型保存在索引。

登记 DEVTECH 或 ARD 时，运行 `project-state register artifact <文稿路径> --kind core:code-architecture`。

更新 Spec 时沿用已有身份。每次登记检查退出码为 0 与 `ok: true`，成功后才回填 ID 或继续依赖该身份的登记；状态不确定时先通过 `project-state list`、`locate` 或 `related` 核对既有节点。具体参数与选项参考 `project-state <子命令> --help`。

`docs/research/` 中的研究文档为非正式内容，不进行登记。

## 架构可视化汇报

新建或修订 ARD 或 Implementation Spec 后，派发不继承当前会话上下文的独立 subagent 生成供用户审阅的可视化报告。ARD 单独成页，Implementation Spec 按 Module 单独成页。

1. **派发**：向 subagent 提供维护后的文档、必要引用（修订时可附文档差异，供标注变更），并且告知 subagent 需要遵守的汇报规则文件路径：
   - 通用规则：[报告通用指引](references/report-guide.md)
   - 专项规则：ARD 使用[ARD 报告指引](references/ard-report.md)，Implementation Spec 使用[Spec 报告指引](references/implementation-spec-report.md)
2. **交付**：subagent 按指引生成单页 HTML，返回成品路径与核对摘要。主 Agent 在回复中直接附上链接，交由用户审阅。

可视化汇报的规则交由 subagent 独立读取执行，主 Agent 仅负责派发与接收成品，不额外介入汇报细节。

## 工作边界

- 探索类任务的结论与产出保留在 `docs/research/`，不自动升级为正式文档，不登记架构身份。
- 编写正式 DEVTECH、ARD 或 Implementation Spec 时可参阅 `docs/research/` 中的研究内容作为输入，但正式文档不应链接引用研究草稿，以保持正式定稿与设计探索的清晰边界。
- 架构实体登记仅在获授权的正式交付时执行。
