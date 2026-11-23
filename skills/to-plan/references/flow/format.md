# Plan 正文与目录（Flow 模式）

沿用项目目录约定；无约定时使用 `docs/plans/<label>/`。

```text
summary.md
tasks/
  T01/
    task.md
    result.md     # 有必要时保存交付说明
    review.md     # 有必要时保存审核结论
    evidence/     # 仅存放通过验收的最终关键证据
plan.json         # validate --sync 生成结构快照，状态命令维护进展
```

`summary.md` 写整体目标、范围、正式依据、Task 拓扑与 Stub 详情及总体验收。Task 是独立交接入口，正文写本次实际工作与判断条件。`plan.json` 保存声明快照与当前状态，不复制工作要求或交付证据。

## summary 的结构与依据

新建的 Flow 模式 `summary.md` 在顶部声明 YAML 头：

```yaml
---
plan-type: flow
---
```

未包含 `plan-type` YAML 头的历史 Plan 默认仍按 `flow` 模式兼容。

`summary.md` 统筹跨 Task 的全局信息，按以下板块组织正文：

| 内容 | 正文内容 |
| --- | --- |
| 目标与范围 | 本次 Plan 的整体目标、交付范围与授权边界 |
| 正式依据 | 关联决策记录、Spec、公共契约及维护源的路径与章节定位 |
| Task 拓扑与交接 | Task 依赖关系图（按需）与 `<!-- harness:stub Sxx -->` 详情块 |
| 总体验收 | 全部 Task 完成后用于整体审核的可观察判据与必要验证入口 |

已有正式依据通过链接定位，不在 `summary.md` 中大段复抄既有决策、协议正文或单 Task 的实施细节。所选 principle 直接按职责分发至各 Task 的“相关 principle”章节；仅在整体审核确需额外专业方法时，于总体验收写明读取入口与条件。跨 Skill 的通用执行规则、规划自检命令与规划期的瞬时工作区状态不写入 `summary.md`。

## Task 的内容结构

| 内容 | 正文内容 |
| --- | --- |
| 目标与边界 | 当前 Task 工作目标、职责边界及交接 |
| 输入与定位 | 相关文件与章节、用途、读取条件、缺项影响 |
| 相关 principle | 当前 Task 开始工作前应加载并阅读的 principle ID |
| 验收标准 | 预期产出、工作结果、边界处理、验证入口和交付证据 |
| 必要流程（按需） | 有依据的必要动作、判断分支和依赖顺序，区分强制要求与推荐方法 |

将当前 Task 应阅读的 principle ID 以 Markdown 列表固定写入“相关 principle”章节，只列完整 ID，不附加选型理由。`workbook` 按工作阶段或条件指定必读与条件 principle 时，规划者判断当前 Task 是否适用，并将适用的完整 ID 列入该章节。

正文只写当前 Task 特有的工作要求、特定登记或工具调用参数及验收判据，不复述 `execute-task`、`execute-plan` 等 Skill 已定义的通用动作。确有不可偏离的操作流程，或需说明复杂的条件、依赖与状态关系时，使用 Mermaid 图或类 Python 伪代码进行结构化表达，避免使用模糊的语言描述流程。

```yaml
---
dependsOn: [T01]
specs: [artifact_guide]
installs: []
fills:
  - {id: S01, name: 操作说明}
uses: []
---
```

Task 编号来自目录，格式为 T 加数字。每个 Task 声明 installs、fills、uses，未涉及的项写空数组。三项中的每条只写 Stub 编号与名称，名称应与 summary 一致。dependsOn 和 specs 可省略；workspace 只在非默认工作目录时填写。specs 引用已登记文稿的稳定身份；章节、理由与具体约束写正文。Plan 和 Task 自身没有 Registry 登记。

| 声明 | 含义 |
| --- | --- |
| installs | 本 Task 交付 Stub 的结构与交接约定，验收完成后进入 installed |
| fills | 本 Task 装填 Stub；开工前该 Stub 已 installed，验收完成后进入 filled |
| uses | 开工前该 Stub 已 installed；不会改变 Stub 状态 |
| dependsOn | 开工前指定 Task 均为 done；等待完整成果时指向装填 Task |

## Stub 的完整要求

围绕 Plan 的核心工作考虑划定 Stub，按所选 workbook 的要求确定范围；没有明确要求时，结合工作目标、成果结构和现状判断。在 Flow 模式中，需通过 `plan-toolkit` 跟踪两阶段状态的 Stub 恰有 1 个安装 Task、1 个不同的装填 Task。一个 Task 可以承担多个 Stub 的工作，但不同时安装和装填同一 Stub。

```markdown
<!-- harness:stub S01 -->
### S01 操作说明
安装要求：确定章节结构、术语、输入材料与验收约定。
装填要求：补齐操作步骤与示例，满足本节的完整文稿验收。
交接位置：docs/guides/operation.md，下游从该位置读取结构与正文。
<!-- /harness:stub S01 -->
```

每块首标题固定为 `### 编号 名称`。编号为 S 加数字，在 Plan 内唯一。正文写实际边界、安装验收、装填验收与产物位置。标记应成对且不嵌套。执行者只读取其 Task 关联的 Stub 块，不默认通读全部 Stub。

fills 已隐含等待安装，不必再在 uses 中重复同一 Stub。uses 可使用已验收的结构与约定，不代表完整内容已交付；等待完整成果使用 dependsOn。共享产物的修改竞争仍通过真实依赖或明确顺序处理。

## 定义与状态

直接编辑 summary 和 tasks，再运行 `plan-toolkit validate <Plan目录> --sync`。工具从文稿生成 plan.json 的声明快照，保留已有状态、note 与 reason；新增 Task 为 pending，Stub 状态从生产者的 done 记录推导。不要手抄快照或手改状态。

同步结果按以下分支处理：

```python
while True:
    退出码, 结果 = 运行("plan-toolkit validate <Plan目录> --sync")
    if 退出码 == 0 and 结果["ok"] and 结果["data"]["valid"]:
        break
    if 错误可通过本次文稿修订解决:
        按错误中的问题定位修正文稿()
    else:
        交付实际错误与恢复条件()
        return
```

- 同步只在候选通过检查后写入。状态损坏、正在执行或已完成 Task 的调度声明变动、已开工 Task 被删除时，不会静默覆盖进展。
- 改变已完成工作时优先使用后续 Task。
- 已 done 的 Plan 要增加工作时，先由调度者 mark rework，再编辑定义。
