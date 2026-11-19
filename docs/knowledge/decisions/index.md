# 项目决策索引看板

本看板维护项目架构决策记录（ADR）的分类索引与快速导航。

## 原则体系与知识规范

- [`principle-atomicity.md`](principle-atomicity.md)：确立原则两级目录结构、单判断原子化标准，以及 core 域与 game 扩展原则的具体拆解全景。
- [`core-principle-atomicity.md`](core-principle-atomicity.md)：core 编程原则原子化拆解摘要与历史审计锚点。（已归并至 [principle-atomicity.md](principle-atomicity.md)）
- [`game-principle-atomicity.md`](game-principle-atomicity.md)：game 扩展原则原子化拆解摘要与历史审计锚点。（已归并至 [principle-atomicity.md](principle-atomicity.md)）
- [`principle-draft-import.md`](principle-draft-import.md)：划分原则草稿提炼与正式入库的职责边界，由 handbook 内部封装通用的项目资源声明模块。

## 架构协同与方法解耦

- [`workbook-and-plan-decoupling.md`](workbook-and-plan-decoupling.md)：确立认知资产层与编排脚手架层的正交解耦，允许 workbook 在轻量确定性工作中自调度直行。
- [`extension-workbook-project-integration.md`](extension-workbook-project-integration.md)：确立“扩展声明重点、项目落地准则与工具”的控制反转架构，放弃抽象的证据插槽实体。
- [`game-audit-design.md`](game-audit-design.md)：game 扩展改造核心决策，以 Spec 网络组织玩法并取消独立 GDD，建立按需加载与先核验后实施机制。

## 工具契约与交互体验

- [`project-state-query-views.md`](project-state-query-views.md)：分离单实体定位与一跳关联查询，精简公共实体视图，并取消 Feature 自动展开 Module 文稿。
- [`cli-experience.md`](cli-experience.md)：规范 `plan-toolkit inspect` 精简视图与 `handbook load` 多 ID 批量读取，退役 principle 的 `includes` 级联支持。

## 工程基建与部署优化

- [`scripts-optimization.md`](scripts-optimization.md)：规范部署回退锁机制，将 Python 依赖构造交由已有工具管理，并建立 CI 多平台分层验收。
