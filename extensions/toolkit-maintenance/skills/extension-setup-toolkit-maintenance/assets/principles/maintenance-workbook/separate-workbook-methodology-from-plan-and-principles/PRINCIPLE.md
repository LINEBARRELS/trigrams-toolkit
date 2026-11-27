---
description: 创建、修订或审核 WORKBOOK.md 的章节结构、模式中立性与职责边界时使用。
---
# 将工作方法、 Plan 工作模式及原则分离

`WORKBOOK.md` 应作为自洽且模式中立的可执行工作方法，与具体 Plan 模式语法及 `principle` 判断细则保持清晰分离。

组织 `WORKBOOK.md` 时应遵循以下边界：
- 正文使用基础的 “适用与输入、必要工作流程、工序切分与交接、产出与验收” 四段排版（按需附“工作约束”），区分已验证做法与候选方案。
- 不应写入特定 Plan 模式的文件或操作指令（如 `summary.md`、`task.md`、`plan.json`、`stub-review.md`、`review.md`、`plan-toolkit` 或“写入 Plan 正文”）。
- 由 `principle` 承担的细粒度判断规则与数值规格，不在 workbook 中堆叠细节工作规则
  - 通过 `includes` header 声明 workbook 本身的配套相关 principle ID
  - 在规则标签中声明在具体执行、审核或者调度时需阅读的 principle ID
- YAML 头的 `name`、`description` 与目录首段 `scope` 应指向一致并与同类 `workbook` 区分；配套参考放 `references/`，模板放 `assets/`，私有脚本放 `scripts/`。
