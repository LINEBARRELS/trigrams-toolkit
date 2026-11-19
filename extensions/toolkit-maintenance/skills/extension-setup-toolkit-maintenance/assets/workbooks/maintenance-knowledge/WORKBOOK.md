---
name: 知识库与 principle 审核
description: 审核当前知识分类、principle 范围、内容切分和冲突，提出可定位的归属及修订候选。用于整理已有知识结构或核对 principle 变更，历史问题通过 why、effect 调查。
resourceId: toolkit-maintenance:workbook:maintenance-knowledge
includes:
- toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence
- toolkit-maintenance:principle:maintenance-knowledge/separate-normative-rules-from-guidance-and-history
---

# 知识库与 principle 审核

## 适用与输入

取得当前项目规则入口、知识目录、待审 principle ID 或路径，以及本次要解决的问题。默认执行只读静态审核，评估文稿结构与引用关系；需要历史背景或变更影响时，委托 why 或 effect 调查并取得带来源的结论。

## 必要工作流程

1. 对照项目导航与资源目录，定位规则的权威正文与读取入口；依据必读原则区分现行规范、历史选择、复盘记录、模块非强制建议与单次任务条件，标明错放与重复项。
2. 运行 `handbook list --kind principle --scope maintenance-knowledge --scope maintenance --scope maintenance-document`，按本次任务从索引选择并 `handbook load` 所需条件原则：
   - 拆分、合并或审核 principle 边界时，加载 `maintenance-knowledge/keep-principles-independently-applicable` 与 `maintenance-knowledge/keep-principles-brief-and-complete`。
   - 创建或修订 principle 名称与描述时，加载 `maintenance-knowledge/name-principles-by-their-decision`。
   - 安排或核查原则按需读取步骤时，加载 `maintenance-knowledge/select-principles-by-task-relevance`。
   - 涉及资源移动、目录改名或身份变更时，加载 `maintenance-knowledge/sync-active-references-on-identity-change` 与 `maintenance/keep-reference-chains-reachable-and-complete`。
   - 审核或修订正文表达与跨层边界时，从 `maintenance-document` 选取对应原则。
3. 核查 principle 入口目录名、scope、名称、description 与正文内容的一致性；头信息只接受 description，组合加载由 workbook 的 includes 声明。用 `handbook scopes` 和 `handbook list` 核对领域分类；涉及目录改名时，用派生的新 ID 执行 `handbook load`，核对当前引用迁移、路径引用和安装入口，再运行 `handbook validate`。
4. 针对问题提出保留、合并、移动、退役或修订候选，说明对引用方与在途工作的影响。

## Task 切分与交接

审核由 general Task 交付。需要持续整改时，按问题共因切分审核、整改与复验 Task，通过显式 `dependsOn` 传递完整成果：整改消费已确认问题和修改授权并更新唯一维护源，复验以整改后的实际材料重验原问题与受影响引用。principle 候选经 `principle-maintenance` 提交用户审定后生效。

## 产出与验收

交付内容归属、问题清单、修订建议、受影响引用与未验证项。报告明确指出问题位置与去向建议，未验证范围单独说明。
