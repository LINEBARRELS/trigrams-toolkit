# game 扩展接入说明

首次接入或增补 game 时，按 setup 正文在对应步骤使用本说明。

## 接入前提

1. 在项目根确认 `harness-install` 已装配 `.agents/extensions/game/`。`handbook` 与 `project-state` 从快照发现 `game:*` 资料与 `game:gameplay-spec`／`game:composes`。
2. 执行依赖游戏能力的工作前，确认项目已通过 Vercel skills 安装 `extension-setup-game`、`game-designer` 与 `art-designer`。

## 文档与路径规范

基础文档沿用项目既有路径；新项目使用 core 默认位置。

| 文稿 | 推荐路径 | 职责与读取时机 |
| --- | --- | --- |
| PRODUCT | `PRODUCT.md` | 产品定位、全局业务术语、版本目标、阶段体验与发布范围；确定玩法目标时读取 |
| gameplay-spec | `docs/gameplays/` | 正式玩法定稿：维护局部术语、实体状态域、核心内循环、组合约束及验收；设计或实现对应玩法时读取 |
| 玩法研究草稿 | `docs/research/gameplay/<topic>/` | 按探索主题归集玩法设计探索、候选机制对比与试玩分析；保持研究身份，不登记正式 Registry |
| DESIGN | `DESIGN.md` | 游戏 UI／UX、操作映射、HUD 布局与交互表达；设计操作和界面时读取 |
| GAME-VISUALS | `docs/GAME-VISUALS.md` | 世界、角色、视觉语言、镜头、光影、动画与场景可读性；设计游戏表现时读取 |
| DEVTECH、ARD | 沿用 core 位置 | 保持项目既有技术架构，仅在涉及游戏引擎、渲染管线或专用基础设施时记录 |

## 执行动作与 AGENTS.md 装配

1. **目录与文稿创建**：
   - 仅对已确定的正式玩法创建 `docs/gameplays/`，对尚未定稿的探索草稿按主题使用 `docs/research/gameplay/<topic>/`，对明确需要表现设计的范围创建 `docs/GAME-VISUALS.md`；严禁创建无实际内容的空占位文件。
   - 在 `PRODUCT.md` 中补充阶段体验与版本目标，按需补充跨玩法通用的业务术语。
2. **AGENTS.md 合并**：
   - 在“项目结构”的文档表中按实际范围补充或更新 `DESIGN.md` 与 `docs/GAME-VISUALS.md`，在路径表中合入 `docs/gameplays/` 与 `docs/research/gameplay/`，标注各自读取时机；不列入不存在的路径或加设“适用条件”列。
   - 在“项目约束 → 项目术语 → 术语检索说明”中合并两级路由：全局业务术语指向 `PRODUCT.md`，各玩法局部术语指向 `docs/gameplays/` 中对应 `gameplay-spec` 内的定义。
   - 上述目录、路径与术语路由均并入 `core:workbook:project-setup` 的对应原子工作与最终 `AGENTS.md` 收敛步骤，不重复编写独立安装流。

## 存量项目迁移

以下领域资料的调查与处置并入 `core:workbook:project-setup` 工作 5 的建议清单（`migration/checklist.md`），仅在用户确认执行时落盘：

1. **迁移 gameplay-spec 与研究草稿**：
   - 将旧 `docs/gameplay-specs/` 下已定稿的正式稿移入 `docs/gameplays/`，尚未定稿的探索草稿按主题移入 `docs/research/gameplay/<topic>/`，修复内部相对链接。
   - 对正式稿运行 `project-state register artifact <新路径> --kind game:gameplay-spec` 保持原身份，并用 `project-state relate <宿主ID> game:composes <组件ID>` 维护组合关系。
   - 存量在途工作引用旧 `game:workbook:gameplay-exploration` 或 `game:workbook:gameplay-development` 时，统一承接至 `game:workbook:gameplay-design`。
2. **拆解旧大部头 GDD**：
   - 核心循环与独立机制拆入独立 `gameplay-spec`，跨玩法互动归入桥梁 Spec，阶段目标合入 `PRODUCT.md`；退役原始文稿按清单移入 `docs/archives/game-designs/`，与代码 Implementation Spec 分别整理。

## 验收要求

1. 结构与导航：`AGENTS.md` 中引用的游戏文档与目录全部实际存在，无死链或空占位声明。
2. 资源可用性：运行 `handbook validate` 确认扩展快照通过校验，且 `game` 的 principle 与 workbook 均能正常发现与加载。
3. 状态一致性：若涉及玩法 Spec 迁移或登记，运行 `project-state validate` 确认无破损实体或悬空关系，并对后续引用的正式 Spec 运行 `project-state locate <真实 Artifact ID>` 确认活动正文。
