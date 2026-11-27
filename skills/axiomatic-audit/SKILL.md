---
name: axiomatic-audit
description: 仅在用户显式调用时，基于 MIT 公理设计（独立公理与信息公理）审查代码耦合度。先读 PRODUCT.md 与 ARD，回避其余技术设计文档直击源码，经脚本重排设计矩阵后输出可视化报告。
disable-model-invocation: true
metadata:
  harness-toolkit-type: workflow
---

# axiomatic-audit

只读审查项目的真实代码耦合度。本 Skill 独立内聚，不依赖工具包内其他 Skill 或 CLI。

## 事实边界

- **只读原则**：全程只读代码与入口文档，不修改业务代码、配置或 ARD 文档。
- **输入白名单**：仅读取项目根 `PRODUCT.md`（若存在）以理解产品功能目标，再读取 `docs/ARD.md`（或用户指定的 ARD 路径）获取“架构层 → 模块 → 功能”清单。若目标项目无 ARD，退化为结合 `PRODUCT.md`（或 `README.md` 简介）与源码顶层目录归纳顶层功能需求（FR）与设计参数（DP）。

**警告：** 不应读取 `DEVTECH.md`、`docs/implementation-specs/`、`docs/research/`、`docs/knowledge/`、历史 Plan 或代码注释中的架构叙述来判断耦合关系。技术设计文档的意图描述会误导对真实代码落地的判断。

## 三层审计映射

按用户需求选定一个层级，或自顶向下逐层下钻。默认优先审查 **架构层** 与 **模块**；用户指定单个模块或要求深潜时审查 **功能**。

| 检测层级 | 行 FR（功能需求） | 列 DP（源码载体） | 求解模式 | 理想矩阵形态 |
| --- | --- | --- | --- | --- |
| **架构层 Layer** | ARD 中的 `## <架构层>` 列表 | 归属各层的源码目录群与 `Arch` 底座 | `paired` | 严格下三角阵 |
| **模块 Module** | ARD 中的 `### <module>` 职责与产品变化轴 | 各模块的源码包边界与对外入口 | `paired` | 对角阵或下三角阵 |
| **功能 Feature** | 单个模块下 `- <feature>` 正交清单 | 模块内部类、状态字段与执行管线 | `bipartite` | 对角阵或流水线下三角 |
| **无 ARD 降级** | 结合 `PRODUCT.md` 与源码入口反推顶层 FR | 顶层代码目录与核心包 | `paired` 或 `bipartite` | 对角阵或下三角阵 |

## 工作流程

1. 明确本次检测范围与层级。如果用户未指定，默认覆盖 **架构层** 与 **模块** 两层。
2. 读取 `PRODUCT.md` 理解程序的功能目标，再读取 `docs/ARD.md` 提取层级、模块（含 `（Arch）` 框架模块）与功能清单。如果项目缺少其中任一文件，如实记为缺项或切换无 ARD 降级模式。
3. 阅读[证据判定与解耦手册](references/evidence-rubric.md)，直接查阅源码完成取证。
   - 把 ARD 清单逐项映射到真实源码文件，记录幻影节点（ARD 有而源码无）与野生节点（源码有而 ARD 无）。
   - 同时排查显式依赖 `D` 与隐式变更耦合 `C`。矩阵中的每一条依赖边都应绑定具体 `path:line` 源码证据；无源码证据的猜测不应写入矩阵。
   - 审查范围较大时，可派发只读 subagent 并行采集各模块的源码依赖证据。
4. 将证据写为标准化 JSON 文件（置于项目根 `.tmp/axiomatic-audit/<scope>-input.json`），运行本 Skill 目录下的[矩阵求解脚本](scripts/matrix_solver.py)完成数学重排与判定。不应凭肉眼判断矩阵能否排成下三角阵。
   ```bash
   python "<本 Skill 目录>/scripts/matrix_solver.py" ".tmp/axiomatic-audit/<scope>-input.json" \
     --json-out ".tmp/axiomatic-audit/<scope>-result.json" \
     --md-out ".tmp/axiomatic-audit/<scope>-matrix.md"
   ```
   结果：脚本输出总体评级（`uncoupled` / `decoupled` / `coupled`）、仅显式 `D` 视图与完整 `D + C` 视图的对比、重排后的行列顺序、强连通耦合环（SCC）、越界上三角边与欠定/冗余诊断。
5. 阅读[报告模板与输出约定](references/report-template.md)，结合求解结果与源码证据编写草稿，调用全局 `answer-me-with-html` Skill 渲染单页 HTML 报告。渲染时应附加 `--no-open`，并通过 `-o` 将报告写入项目根 `.tmp/axiomatic-audit/<YYYYMMDD-HHMM>-<scope>.html`。
6. 在终端回复精简总结：耦合评级、显式与完整视图差异、关键耦合环及核心漂移项，并在末尾附上生成报告的可点击路径链接。不应把完整草稿粘贴到终端。
