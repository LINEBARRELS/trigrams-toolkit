---
name: workbook 审核
description: 审核已有 workbook 的选择描述、工作方法、配套文件和任务交接，使用代表性目标检查 Plan 是否可执行与验收。用于修改 workbook 或发布前复核，workbook 定制仍采用 core meta workbook。
resourceId: toolkit-maintenance:workbook:maintenance-workbook
includes:
- toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence
- toolkit-maintenance:principle:maintenance-workbook/structure-workbooks-for-plan-translation
---

# workbook 审核

## 适用与输入

取得待审 workbook ID、元数据、正文及配套文件，提供代表性目标和项目约束。新增方法的调查与定制使用 core 的 meta workbook。

## 必要工作流程

1. 核对入口目录名、scope、name、description 与基础四章结构，依据必读原则 `structure-workbooks-for-plan-translation` 检查领域分类、目标匹配、方法可操作性与配套资源组织。用 `handbook scopes` 和 `handbook list` 核对实际发现结果。
2. 运行 `handbook list --kind principle --scope maintenance-workbook --scope maintenance --scope maintenance-knowledge --scope maintenance-document`，按待审内容选择并 `handbook load` 条件原则：
   - 审核或设计 Task 切分粒度、`dependsOn` 与 Stub 阶段交接时，加载 `maintenance-workbook/split-workbook-tasks-by-deliverable-and-handoff`。
   - 检查 `includes` 必读声明与按需条件读取边界时，加载 `maintenance-knowledge/select-principles-by-task-relevance` 与 `maintenance/keep-reference-chains-reachable-and-complete`。
   - 涉及目录改名或身份迁移时，加载 `maintenance-knowledge/sync-active-references-on-identity-change`。
   - 检查是否机械搬运 principle 正文、硬编码下游 Task 提示词或堆砌防御套话时，加载 `maintenance/keep-one-authoritative-source-per-rule` 及 `maintenance-document` 下的对应原则。
3. 核查配套文件引用、读取条件、`includes` 关联及外部依赖的有效性。涉及目录改名时，用原 ID 执行 `handbook load`，核对身份保留、路径引用和安装入口，再运行 `handbook validate`。
4. 按 workbook 草拟代表性 Plan，验证依赖关系（`dependsOn` 与 Stub 阶段交接）与可转化性。涉及 Plan 声明或交接机制修改时，运行 `plan-toolkit validate <Plan目录> --sync` 校验规范性。

## Task 切分与交接

审核与演练由 general Task 交付。需要整改时按 `dependsOn` 组织修改与复验 Task，整改输入为审核报告，复验输入为修订产物与实测数据。

## 产出与验收

审核报告包含代表性场景、路由判断、定位问题、修订建议与演练结果。分别记录静态格式校验、演练执行记录及未运行范围。
