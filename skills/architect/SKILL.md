---
name: architect
description: 探索技术设计，或维护 DEVTECH、ARD 与代码实现 Spec。用于宏观架构、Module / Feature 边界、公共契约和技术设计变更。
metadata:
  harness-toolkit-type: workflow
---

# architect

使用 `principles` skill，加载 `programming-design-architecture` scope 下的全部原则，并按本次设计目标从 `programming-design-abstraction`、`programming-design-module`、`programming-design-repo`、`programming-pragmatic` scope 中选取适用原则。涉及类型、属性、常量或公共签名声明时，从对应编程语言的 scope 中选取适用 principle。沿用项目 `AGENTS.md` 或已有路径、绑定与标识；新项目无约定时，默认使用 `DEVTECH.md`、`docs/ARD.md`、`docs/implementation-specs/` 和 `docs/research/`。

## 设计与文档

正式文档记录已确定的架构设计；未定方案与设计研讨归入研究目录。动笔编辑文档前使用 `doc-polish`。

- **非正式的设计探索**：当用户的工作目标不涉及维护下面的三种正式文档、仅希望做前期调研时，基于项目现状和设计目标，比较设计候选方案，记录设计研究方案、待裁决问题，保存至 `docs/research/`，基于探索主题创建对应的、可复用专题子文件夹。
- **DEVTECH**：维护技术栈、工程组织、架构层（`Architecture Layer`）清单、宏观职责、依赖方向、所有权与跨模块通用术语。结合应用运行形态，沿外部交互与表现、应用编排、核心业务决策及底层支撑的职责与稳定性差异，垂直切分项目实际所需的架构层。在“应用架构”中列明当前项目的 `Architecture Layer` 清单，界定各层职责边界、单向依赖方向、调用方式及运行环境约束。
- **ARD**：沿用 `DEVTECH` 已确立的 `Architecture Layer` 清单与顺序展示 `Module → Feature` 结构，使用下方格式。`DEVTECH` 未列明当前项目的 `Architecture Layer` 清单或现有层级无法覆盖本次变更时，因缺少稳定的层级划分基准，无法维护 `ARD` 架构树；应先停工、通知用户在 `DEVTECH` 中确立或修订架构层划分。Module、Feature 名称使用 `kebab-case` 格式，职责简述使用用户语言。Feature 按正交行为职责划分。ARD 不列举对应的 Spec；运行 `project-state related <Module ID>`，检查退出码为 0 和 `ok: true` 后，读取 `data.items` 中 Artifact 的 `path`。从 Feature 导航共享资料时，先取 `locate <Feature ID>` 的 `data.moduleId` 或 `related <Feature ID>` 返回的 Module，再查询该 Module。
- **Implementation Spec**：每个 Module 的实现设计集中在一份 Spec，按[模板](references/templates/implementation-spec.temp.md)选用适用章节编写，定义所属 Feature 行为、能力、输入输出、所有权、依赖、公开契约、状态、失败语义与运行约束。

ARD 节点格式如下；按实际结构重复 Module 与 Feature。已登记节点填写真实 ID；尚未登记时省略 ID 括号，登记成功后回填。

```markdown
## <架构层名称>

### <module-name>（<真实 Module ID>）

<Module 职责简述>

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

1. **派发**：向 subagent 提供项目目录、维护后的文档、必要引用与指引路径（修订时可附文档差异，供标注变更）：
   - 通用规则：[报告通用指引](references/report-guide.md)
   - 专项规则：ARD 使用[ARD 报告指引](references/ard-report.md)，Implementation Spec 使用[Spec 报告指引](references/implementation-spec-report.md)
2. **交付**：subagent 按指引生成单页 HTML，返回成品路径与核对摘要。主 Agent 在回复中直接附上链接，交由用户审阅。

## 工作边界

- 探索类任务的结论与产出保留在 `docs/research/`，不自动升级为正式文档，不登记架构身份。
- 禁止在 DEVTECH、ARD 或 Implementation Spec 中引用 `docs/research/` 中的研究文档，避免混淆正式定稿与设计探索的边界。
- 架构实体登记仅在获授权的正式交付时执行。
