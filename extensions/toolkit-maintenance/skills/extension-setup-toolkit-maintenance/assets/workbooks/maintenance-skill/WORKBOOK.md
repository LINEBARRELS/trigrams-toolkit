---
name: Skill 审核
description: 审核已有 Skill 的触发条件、主类型、职责、资料载入与能力调用，交付问题和明确的修订范围。用于局部修改或发布前检查，可在已有授权内整改并复验。
resourceId: toolkit-maintenance:workbook:maintenance-skill
includes:
- toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence
- toolkit-maintenance:principle:maintenance-skill/align-skill-type-with-trigger-and-delivery
---

# Skill 审核

## 适用与输入

取得目标 Skill、审核目的、当前修改范围和代表性使用场景。整体审核覆盖适用模式；局部修改检查受影响的分支和依赖。默认执行只读静态检查。

## 必要工作流程

1. 比较 `description`、主类型声明、入口正文和实际交付，依据必读原则 `align-skill-type-with-trigger-and-delivery` 核对触发条件、主类型及流程表达是否准确。
2. 运行 `handbook list --kind principle --scope maintenance-skill --scope maintenance --scope maintenance-tooling --scope maintenance-document`，按目标 Skill 特征选择并 `handbook load` 条件原则：
   - 检查通用 Skill 的跨领域边界、跨 Skill 协作或人称范式时，加载 `maintenance-skill/keep-skills-focused-and-composable` 与 `maintenance/keep-reference-chains-reachable-and-complete`。
   - 审核新建、更新或归档正式架构文档（`docs/`）的 Skill 时，加载 `maintenance-skill/specify-artifact-lifecycle-in-document-skills`。
   - 审核 Skill 正文中的 CLI 调用说明时，加载 `maintenance-tooling/specify-cli-action-context-not-flag-manuals`。
   - 检查文稿防腐、内部细节外泄或跨层重复时，从 `maintenance-document` 与 `maintenance/keep-one-authoritative-source-per-rule` 选择对应原则。
3. 按主类型检查资料加载与调用链，选用代表性输入验证资料分流、工具调用与结果判断逻辑，检查是否存在无条件加载全量文件或隐式级联调用的情况。
4. 归并同类问题，定位负责文件、建议修改项、受影响调用方与验证方式。

## 工序切分与交接

只读审核作为独立 Stub 交付。只授权审核时交付报告；获得修改授权时，按“审核 → 整改 → 复验”工序衔接：整改消费审核报告并修改唯一维护源，复验消费修订后的文稿与实测证据。

## 产出与验收

交付审核范围、分类依据、结论清单、拟修改文件与验证限制。问题明确指出位置与证据，区分静态分析与动态运行试验；未验证项单独列明。
