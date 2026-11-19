---
name: workbook
description: 仅在被明确指定时使用。按当前任务查询并加载适用的 workbook（特定工作类型的标准作业方法），用于明确执行流程、阶段拆分、交接要求与验收标准。
metadata:
  harness-toolkit-type: content-loading
---

# workbook

在项目根目录运行 `handbook`。

1. 运行 `handbook list --kind workbook`，按当前需求从返回的资源 ID 与描述中选择条目。已知 ID 时跳过查询。
2. 运行 `handbook load <ID> [<ID> ...]` 加载并读取对应正文；配套材料按正文条件读取。已读且仍适用的内容不必重读。
3. 返回选中 ID、来源与适用方法；没有适用条目时说明缺口。加载方法不启动其中的工作。

按分类查询可用 `handbook scopes --kind workbook` 和 `list --scope <分类>`；其他参数查 `handbook <子命令> --help`。
