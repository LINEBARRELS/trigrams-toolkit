# game 扩展接入说明

本说明为 `extension-setup-game` 的配套细则，供 `core:workbook:project-setup` 在工作 4（扩展管理）与工作 5（仅用户明确要求时）按节查阅。

## 资源与依赖明细

1. 在项目根确认 `harness-install` 已装配 `.agents/extensions/game/`。`handbook` 与 `project-state` 从快照发现 `game:*` 资料与 `game:gameplay-spec`／`game:composes`。
2. 执行依赖游戏能力的工作前，确认项目已通过 Vercel skills 安装 `extension-setup-game`、`game-designer` 与 `art-designer`。

## 目录与项目级文档明细

基础文档沿用项目既有路径；领域增量如下：

| 文稿 / 目录 | 推荐路径 | 职责与读取时机 |
| --- | --- | --- |
| PRODUCT（补充） | `PRODUCT.md` | 补充阶段体验、版本目标、发布范围与跨玩法全局业务术语；确定玩法目标时读取 |
| DESIGN（补充） | `DESIGN.md` | 承载游戏 UI／UX、操作映射、HUD 布局与交互表达；设计操作和界面时读取 |
| GAME-VISUALS（新增） | `docs/GAME-VISUALS.md` | 仅在明确需要表现设计时创建；维护世界、角色、视觉语言、镜头、光影、动画与场景可读性 |
| gameplay-spec 目录 | `docs/gameplays/` | 正式玩法定稿：维护局部术语、实体状态域、核心内循环、组合约束及验收；设计或实现对应玩法时读取 |
| 玩法研究草稿目录 | `docs/research/gameplay/<topic>/` | 按探索主题归集玩法探索、候选机制对比与试玩分析；保持研究身份，不登记正式 Registry |
| DEVTECH、ARD | 沿用 core 位置 | 保持项目既有技术架构，仅在涉及游戏引擎、渲染管线或专用基础设施时记录 |

### AGENTS.md 增量与移除规则

- **接入合并**：在“项目结构”文档表中补充实际存在的 `DESIGN.md` 与 `docs/GAME-VISUALS.md`，在路径表中合入 `docs/gameplays/` 与 `docs/research/gameplay/`，不列入不存在的路径或加设“适用条件”列；在“项目约束 → 项目术语 → 术语检索说明”中合并两级路由（全局业务术语指向 `PRODUCT.md`，各玩法局部术语指向 `docs/gameplays/` 中对应 `gameplay-spec`）。
- **移除清理**：卸载 `game` 扩展时，从 `AGENTS.md` 删除上述 `docs/GAME-VISUALS.md`、`docs/gameplays/`、`docs/research/gameplay/` 导航行及玩法局部术语路由，不删除项目已有文稿。

## 存量项目迁移

仅当用户明确要求执行 `core:workbook:project-setup` 工作 5 时，将以下领域调查与处置建议并入 `migration/checklist.md`：

1. **迁移 gameplay-spec 与研究草稿**：
   - 将旧 `docs/gameplay-specs/` 下已定稿的正式稿移入 `docs/gameplays/`，尚未定稿的探索草稿按主题移入 `docs/research/gameplay/<topic>/`，修复内部相对链接。
   - 对正式稿运行 `project-state register artifact <新路径> --kind game:gameplay-spec` 保持原身份，并用 `project-state relate <宿主ID> game:composes <组件ID>` 维护组合关系。
   - 存量在途工作引用旧 `game:workbook:gameplay-exploration` 或 `game:workbook:gameplay-development` 时，统一承接至 `game:workbook:gameplay-design`。
2. **拆解旧大部头 GDD**：
   - 核心循环与独立机制拆入独立 `gameplay-spec`，跨玩法互动归入桥梁 Spec，阶段目标合入 `PRODUCT.md`；退役原始文稿按清单移入 `docs/archives/game-designs/`，与代码 Implementation Spec 分别整理。

## 验收要求

1. **资源可用性**：运行 `handbook validate` 确认 `.agents/extensions/game/` 快照通过校验，且 `game` 的 principle 与 workbook 均能正常发现与加载。
2. **结构与导航**：`AGENTS.md` 中引用的游戏文档与目录全部实际存在，无死链或空占位正文。
3. **状态一致性**：若涉及玩法 Spec 迁移或登记，运行 `project-state validate` 确认无破损实体或悬空关系，并对引用的正式 Spec 运行 `project-state locate <真实 Artifact ID>` 确认活动正文可达。
