---
name: principles
description: 按当前任务查询并加载适用的 principle（特定领域泛用的决策准则与质量规范），用于指导方案设计、实际执行中的取舍判断与成果审查。
metadata:
  harness-toolkit-type: content-loading
---

# principles

在项目根目录运行 `handbook`。

1. 运行 `handbook list --kind principle`，按当前需求从返回的资源 ID 与描述中选择条目。已知 ID 时跳过查询。
2. 运行 `handbook load <ID> [<ID> ...]` 加载并读取对应正文；配套材料按正文条件读取。已读且仍适用的内容不必重读。
3. 返回选中 ID、来源与适用条件；没有适用条目或存在未解决冲突时说明。

按分类查询可用 `handbook scopes --kind principle` 和 `list --scope <分类>`；其他参数查 `handbook <子命令> --help`。
