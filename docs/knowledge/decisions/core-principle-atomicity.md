# core 编程原则原子化拆解

决策日期：2026 年 10 月 27 日。

> [!NOTE]
> 本决策记录已作为领域拆解方案，完整归并至统一决策文件 [principle-atomicity.md](principle-atomicity.md) 的“2. core 领域原则拆解方案”小节。
> 本文件保留历史链接锚点与核心决策摘要，供历史审计追踪与跨文档链接访问。

## 决策摘要

- **拆解规模**：退役 11 个聚合原则入口，重构为 44 条可独立应用的原子原则（设计类 29 条、语言规范类 12 条、基础框架类 3 条）。
- **解耦级联**：解除隐式 `includes` 级联，改由 `programming-development` 与 `programming-exploration` 等 workbook 显式声明必读原则。
- **正文与口径**：设计原则保持英文正文；语言原则内层按特异风险聚类，并将规模统计口径直接并入对应原则正文。
- **全景与设计取舍**：完整背景、架构规则与代价说明见 [原则体系原子化规范与各域拆解全景](principle-atomicity.md)。

## 实施承接

原实施 Plan（`core-principle-atomicity`）已随旧仓归档；现行 core 原则正文以 `skills/principles/principles/` 及 [架构说明](../../../skills/toolkit-steward/references/architecture.md) 为准。
