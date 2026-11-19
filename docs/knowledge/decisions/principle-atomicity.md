# 原则体系原子化规范与各域拆解全景

决策日期：2026 年 10 月 27 日。

## 目的与背景

为了让 Agent 在读取正文前，就能判断当前任务需要哪些原则，并精准组合相关依据，项目对既有 principle 体系实施原子化重构。
此前 principle 多以主题聚合命名，一个入口包含多项判断，且递归 `includes` 会隐式带入整组正文，导致选择粒度过粗、上下文开销大。

2026 年 10 月 27 日，经统一评审决策，确立了两级目录规范、单判断标准与索引去冗机制，并以 `toolkit-maintenance` 为试点验证后，同步在 `core` 核心库与 `game` 扩展域全面完成原子化拆解落地。

---

## 1. 核心架构与元设计规范

### 1.1 目录结构与资源身份
- 统一采用两级目录结构：`principles/<scope>/<principle>/PRINCIPLE.md`。
- 一级目录表示完整 scope，二级英文目录命名具体原则。
- 资源身份由目录组合派生为 `provider:principle:scope/principle`，不另设分类标签。两级目录直接体现层级关系，减少重复元数据。

### 1.2 索引与加载契约
- CLI 索引条目只保留 `resourceId` 与 `description`。原则目录名表达具体取舍，`description` 说明适用情境。
- `handbook load` 保留正文与来源。
- 退役 principle 的 `includes` 级联能力，principle 统一作为加载叶子节点；组合引用关系交由 workbook 声明。

### 1.3 单判断原则与篇幅基线
- 原子原则仅承载一个可独立应用的判断。
- 前提条件与必要例外留在同一正文；具体流程、接口格式与长案例归入各自维护源。
- 试点正文采用最多 15 个非空行、800 个原始字符作为精简预算参考，优先保留必要判断条件，不设僵化门禁。

---

## 2. core 领域原则拆解方案

基于试点经验，将 `core` 内置的 11 个聚合入口重构为 44 条可独立应用的原子原则：

1. **设计原则（保留英文正文，按 `###` 排版区块一对一拆解）**：
   - 退役删除伞入口 `programming-design/design-judgment`（移除 `programming-design` scope），改由编程 workbook 指引按具体设计子域 scope 检索。
   - 保留 `programming-design-layer`（5 条）、`programming-design-module`（5 条）、`programming-design-abstraction`（11 条）、`programming-design-repo`（4 条）、`programming-pragmatic`（4 条）五个 scope，拆解为 29 个独立原则目录。
   - 二级英文目录名扩写为表达具体取舍的动宾或主谓短语（如 `earn-abstractions-from-real-variants`），中文 `description` 末尾保留原规则 key（如 `（abstraction.earned）`）。
   - 正文保持英文原文，剥离原文档顶部的重复 `Usage` 表格与末尾 `Refs` 行，移除 `includes`。
2. **特定编程语言原则（对齐声明／实现阶段，内层按语言特异风险聚类，并入规模统计口径）**：
   - `programming-csharp`、`programming-python`、`programming-typescript-javascript` 三个 scope 下，每门语言拆为 4 条独立原则（声明期 2 条、实现期 2 条），移除原 `references/` 二次跳转目录与隐式 `includes`。
   - 架构声明期（参数计数、文件行数）与编码实现期（有效行、嵌套深度）的规模统计口径直接并入对应原则正文，不单独拆分微型统计条目。
   - 内层聚类贴合语言特异的静态契约与运行时高发风险。
3. **基础编程与规模上限原则（解耦框架与交接）**：
   - 原 `programming/framework-and-handoff` 拆分为 `programming/define-framework-before-implementation` 与 `programming/mark-stubs-and-handoff-notes-in-source`。
   - workbook 在 YAML 头中显式声明必读的框架定义原则；Stub 标识原则与 `programming-scale/keep-code-within-scale-limits` 作为按需读取的条件原则，不再隐式级联。

---

## 3. game 领域原则拆解方案

game 扩展原则全面转向原子化，退役 4 个旧总括入口，拆解为 29 条独立原则：

1. **Scope 与条目划分**：
   - 保留 `gameplay-experience`（10 条）、`gameplay-rules`（8 条）、`gameplay-composition`（5 条）、`runtime-evidence`（6 条）四个 scope。
   - 新目录名表达具体取舍，`description` 说明触发情境，必要前提与例外随同一判断保留。
2. **职责边界与依赖解耦**：
   - 原则仅保管判断标准；组合角色说明归 gameplay-spec 格式资料，采集和跨 Task 交接步骤归已有 workbook 与 Godot 方法。
   - game 扩展保持独立，不因原则原子化引入对 `toolkit-maintenance` 扩展的依赖，公共协议与安装方式保持现状。
3. **Workbook 适配**：
   - workbook 仅通过 `includes` 声明每次执行必需的基础原则，条件判断按具体任务从相应 scope 选择，不因拆分将整组新条目固定载入。

---

## 承受的代价与演进影响

- **ID 变更与引用同步**：原则目录改名或 scope 调整改变了派生 ID，需同步更新所有关联 workbook（如 `programming-development`、`programming-exploration` 及 game 的三份 workbook）、工具契约说明及自动化回归测试。
- **人工核验成本**：原子化拆分边界与读取分支依赖人工核对，结构校验无法替代内容有效性判断。
- **外部迁移**：已完成的历史记录保留当时事实，外部项目的待迁移事项另行交接。

---

## 依据与承接

依据 2026 年 10 月 27 日原则原子化专项评审确认的架构方案与拆解决定。原实施 Plan（`principle-atomicity`、`core-principle-atomicity`、`game-principle-atomicity`）已随旧仓归档；现行结构与加载契约以 [Handbook 协议](../../../src/trigrams_toolkit/resources/handbook/PROTOCOL.md) 与 [架构说明](../../../skills/toolkit-steward/references/architecture.md) 为准。
