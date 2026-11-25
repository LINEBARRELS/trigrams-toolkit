---
name: 玩法设计
description: 围绕体验目标构建玩法内循环，明确术语、实体状态域、规则结算、组合边界与行为验收；适用于玩法探索研究与正式 gameplay-spec 制定及修订。
resourceId: game:workbook:gameplay-design
includes:
- game:principle:gameplay-experience/align-player-goals-with-target-experience
- game:principle:gameplay-experience/let-loop-results-shape-later-decisions
- game:principle:gameplay-composition/make-each-spec-describe-complete-operation
- game:principle:gameplay-rules/define-rule-entities-and-legal-state-domains
- game:principle:gameplay-rules/make-state-transition-results-decidable
- game:principle:gameplay-rules/specify-outcomes-when-conditions-fail
- game:principle:gameplay-rules/derive-acceptance-from-owned-gameplay-rules
---

# 玩法设计

## 适用与输入

取得本次设计目标、体验问题、`PRODUCT.md` 约束、相关正式 `gameplay-spec` 及用户想法。需要外部机制案例时按问题读取[外部资料索引](references/sources.md)。修订既有正式玩法时，沿其稳定身份定位正文、直接组合关系和实际消费者。

## 必要工作流程

1. 明确玩家目标、目标体验与本机制负责范围，定位参与组合的既有正式 Spec。涉及机制组合与影响追踪时，运行 `handbook list --kind principle --scope gameplay-composition` 并按需 `handbook load`：
   - 跨玩法新增互动加载 `keep-cross-mechanic-interactions-in-bridge-specs`；
   - 共享机制复用与冲突裁决加载 `preserve-shared-mechanic-contracts-in-composition`；
   - 文稿组合依赖整理加载 `record-only-direct-acyclic-spec-dependencies`；
   - 修改共享机制时，在项目根运行 `project-state related <ID> --direction incoming`，加载 `trace-mechanic-changes-through-actual-consumers` 从直接消费者逐层追踪受影响组合。
2. 按共用[格式与填充规范](references/gameplay-spec.md)及[模板](assets/templates/gameplay-spec.temp.md)，声明本玩法新增的专有术语、实体、状态合法值域、操作标识与共享范围，写明跨步骤成立的状态约束与派生关系。维护状态不变式或派生值时，运行 `handbook load game:principle:gameplay-rules/keep-state-invariants-and-derived-values-consistent`。
3. 构建 3–5 步的核心内循环（感知机会／触发 → 玩家选择／投入 → 规则裁决 → 状态结算 → 结果反馈并塑造后续决策），绘制 Mermaid 流程图，并按循环步骤就地展开触发输入、状态转移规则（`R-xx`）、失败与边界分支、互动反馈（`F-xx`）。按具体设计问题运行 `handbook list --kind principle` 并从对应 scope 加载条件原则：
   - 比较选择代价与信息揭露时机、评估挑战匹配度、重复操作意图、成果识别、高压应对空间、奖惩节奏，或从试玩行为诊断设计偏差时，从 `gameplay-experience` 选取对应原则（`give-choices-understandable-costs-and-consequences`、`reveal-decision-information-at-the-needed-time`、`match-challenge-to-player-readiness`、`give-repeated-actions-an-experience-purpose`、`make-action-outcomes-recognizable`、`preserve-response-options-under-pressure`、`tune-rewards-and-penalties-to-experience-rhythm`、`diagnose-playtest-deviations-from-observed-behavior`）；
   - 归集单次结算与多阶段效果、裁决临界阈值／执行顺序／初始化／重复触发，或对齐操作输入语义与反馈映射时，从 `gameplay-rules` 选取对应原则（`group-complete-effects-by-settlement`、`define-boundaries-that-change-gameplay-rulings`、`align-player-input-and-feedback-with-rules`）。
4. 按成熟度完成探索或正式设计：
   - **探索与研究草稿**：方向待定或比较多个候选机制时，交付候选内循环差异、体验收益与代价、取舍依据及未决问题。研究稿保持研究身份，以普通链接指向既有正式 Spec。
   - **正式玩法定稿**：方向已选定且规则收敛时，从确定规则提炼可判定的行为验收，核对操作与反馈语义及相关表达文稿。研究草稿转正时重新核对术语状态域、内循环失败分支与组合关系并取得新身份；既有正式 Spec 更新沿用原 ID。
5. 对正式定稿整理 Artifact 身份与 `game:composes` 直接组合关系，按 `game-designer` 规范完成登记。

## 工序切分与交接

按内聚的玩法问题或正式 Spec 结果划定 Stub 与工序。候选比较与取舍可在同一 Stub 完成；独立试玩需消费完整原型时，明确先后依赖并交接原型位置、场景、输入与观察目标。

共享机制变更时，同步交接受影响的消费者和在途工作。

## 产出与验收

探索工作交付候选比较、取舍依据、参考来源与未决问题。正式设计交付定稿的 `gameplay-spec`、行为验收及已同步的身份与组合关系；新增术语与实体状态域清晰，核心内循环闭合，当前范围的规则与失败分支可判定，直接组合约束兼容，已有身份保持稳定，正文与已登记关系一致。
