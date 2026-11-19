# game 原则原子化拆解

决策日期：2026 年 10 月 27 日。

> [!NOTE]
> 本决策记录已作为领域拆解方案，完整归并至统一决策文件 [principle-atomicity.md](principle-atomicity.md) 的“3. game 领域原则拆解方案”小节。
> 本文件保留历史链接锚点与核心决策摘要，供历史审计追踪与跨文档链接访问。

## 决策摘要

- **拆解规模**：保留 `gameplay-experience`、`gameplay-rules`、`gameplay-composition`、`runtime-evidence` 四个 scope，退役 4 个旧总括入口，拆解为 29 条独立原则。
- **职责划分**：原则保管判断标准，Spec 网络负责表达组合角色，跨 Task 交接与采集步骤归入 workbook 与 Godot 配套方法。
- **加载解耦**：workbook 仅声明执行必需的基础原则，条件判断按具体任务从相应 scope 选择加载。
- **全景与设计取舍**：完整背景、架构规则与代价说明见 [原则体系原子化规范与各域拆解全景](principle-atomicity.md)。

## 实施承接

原实施 Plan（`game-principle-atomicity`）已随旧仓归档；现行 game 原则正文以 `extensions/game/skills/extension-setup-game/assets/principles/` 及 [game 扩展接入说明](../../../extensions/game/skills/extension-setup-game/references/project-integration.md) 为准。
