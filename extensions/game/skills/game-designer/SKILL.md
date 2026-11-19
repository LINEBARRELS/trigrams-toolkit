---
name: game-designer
description: 探索玩法、细化内循环规则与组合约束，管理研究草稿与正式 gameplay-spec；用于玩法讨论和正式设计。
metadata:
  harness-toolkit-type: workflow
---

# Game Designer

读取 `PRODUCT.md`、项目文档导航与相关正式 `gameplay-spec`，明确体验目标、玩法边界及组合约束。现状结构、历史取舍原因或消费者与在途工作影响不明时，携具体问题、目标 ID 或路径及已有材料分别调用 `how`、`why` 或 `effect`。

## 工作方法与产出分流

玩法讨论、候选机制比较、规则细化与修订统一通过 `workbook` 加载 `game:workbook:gameplay-design`，按任务成熟度定义并分流产出目标，严格区分“研究草稿”与“正式定稿”（动笔编辑文档前使用 `doc-polish`）：

| 阶段与请求 | 产出定位与目标路径 | 交付要求与身份边界 |
| --- | --- | --- |
| **玩法设计探索**（讨论想法、比较候选机制、分析试玩偏差、寻找参考） | **研究草稿**：保存至 `docs/research/gameplay/<topic>/` | 按探索主题创建或复用专题子文件夹，收纳对应玩法研究。聚焦候选内循环、体验代价对比、取舍依据与未决问题。保持草稿与研究身份，不登记正式 Artifact 身份或 `game:composes` 关系；以普通链接引用既有正式 Spec |
| **正式玩法定稿**（细化已选定方向、冻结确定规则、修订既有正式玩法） | **正式 Spec**：维护于 `docs/gameplays/` | 按共用格式写清新增术语与实体状态域、核心内循环、分步规则与失败分支、组合约束及行为验收。登记或复用 `game:gameplay-spec` 身份并同步 `game:composes` 关系 |

### 草稿转正与边界约束

- 未经用户确认选定方向并补齐可判定规则前，严禁将 `docs/research/gameplay/` 下的研究草稿直接移入 `docs/gameplays/`。
- 研究草稿转为正式定稿时，清理未决候选分支，核对新增术语、实体状态域、核心内循环结算、失败边界与直接组合约束完整自洽，迁入 `docs/gameplays/` 后登记新的正式 Artifact ID。

## 文档职责

`PRODUCT.md` 维护产品定位、版本目标、阶段体验与全局业务术语；`gameplay-spec` 维护自身边界、局部术语、实体状态域、核心内循环、组合约束、玩家意图、信息获知时机与结算规则。操作映射与界面表达归 `DESIGN.md`，画面与镜头表现归 `docs/GAME-VISUALS.md`。

局部玩法术语在对应 Spec 的“术语、实体与状态”章节定义；跨玩法共享或上升为全局业务概念时上浮至 `PRODUCT.md` 并移除局部重复定义。

## 正式交付与登记

仅对 `docs/gameplays/` 下的正式定稿执行身份与关系登记。交付文稿路径、已有身份、直接组合关系增删及受影响的消费者和 Task。新增正式稿取得新身份；已有正式 Spec 的移动、改名与修订沿用原 ID。

直接设计时，主 Agent 在授权范围内登记；作为 Task 产出时，执行者交付登记信息，由主调度者接收。

1. 运行 `project-state register artifact <路径> --kind game:gameplay-spec [--module <ID>] [--feature <ID>...]`。路径取本次 `docs/gameplays/` 下的正式稿，归属取真实且已确定的 Module／Feature；无技术归属时独立登记。
2. 取得登记返回的 ID，运行 `project-state relate <组合Spec> game:composes <被使用Spec> [--remove]`，按正文同步两端已登记玩法的直接关系。
3. 核对每次退出码为 `0` 与 `ok: true`，成功后再消费身份或继续登记。写入结果不确定时，先用 `project-state` 只读查询核对已发生的写入，再决定继续或报告失败。

玩法规则变化先更新 `docs/gameplays/` 下的正式 Spec 与相关验收，再交接受影响的消费者和在途工作。
