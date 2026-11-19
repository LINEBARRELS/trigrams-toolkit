# Handbook

handbook 提供 workbook 与 principle 的发现、加载和校验，并将已审定原则草稿写入项目正式库。完整契约见 [PROTOCOL.md](PROTOCOL.md)。

| 命令 | 返回与用途 |
| --- | --- |
| `scopes [--kind workbook\|principle]` | 返回当前项目可用 scope，去重并排序 |
| `list [--kind workbook\|principle] [--scope SCOPE]` | 每项只有 resourceId、description；重复 scope 取并集，省略时返回全部 |
| `load ID [ID ...]` | 一次读取多个入口，返回全局去重的正文、名称、来源、路径及 workbook 递归依赖 |
| `validate` | 校验布局、头信息、身份和 includes；返回 checkedSources 与 resourceIds |
| `import-principle FILE --scope SCOPE --name NAME [--replace]` | 写入已审定草稿，返回 resourceId、绝对 entryPath 和 operation（created 或 updated） |

```powershell
handbook scopes --kind principle
handbook list --kind principle --scope programming-design-architecture
handbook load core:principle:programming-design-architecture/separate-business-decisions-from-external-details
handbook validate
```

principle 使用 `principles/<scope>/<principle>/PRINCIPLE.md`。一级目录完整名称是 scope，二级英文小写连字符目录是原则名称。例如 programming-design-architecture 与 programming 是两个平级 scope，筛选精确匹配。ID 派生为 `<source>:principle:<scope>/<principle>`；唯一时可用 `scope/principle` 短名。

```yaml
---
description: 划分表现渲染、外部交互、编排逻辑与业务数据决策职责边界时使用（layer.policy-detail-split）。
---
```

principle 头信息只接受 description，带 includes（包括空数组）返回 invalid_schema。名称和身份从目录取得，改目录后同步当前引用。单条原则只加载自身，长正文和附件仍可使用；正文内的其他资料按条件读取。

workbook 沿用 `<scope>` 或 `<scope>-<topic>` 目录；scope 取第一个连字符前的部分。其 YAML 头保留 name、description、可选 resourceId 与 includes，省略 ID 时由来源、workbook 和目录名派生。目录改名时保留已被引用的显式 ID。includes 可跨 scope 递归包含 workbook 与 principle，principle 为叶子。

业务命令从目标项目根运行，输出 JSON，成功退出码为 0。检查 ok 后使用结果。批量中任一入口失败时整次失败，不输出部分正文。短名歧义返回可直接重试的完整候选 ID。可在任意目录用 `-h` 或 `--help` 查询参数，用 `-v` 或 `--version` 查看工具包版本。

资料来自目标 agent 的全局 `principles`、`workbook`，以及已登记的项目扩展快照与 `docs/resources.json`。用 `--agent` 指定全局 Skill 的宿主，省略时取安装记录或默认 `codex`。资源清单、来源边界和安装说明见协议的“资源清单与安装”。

原则入库前，先审定草稿正文、scope 和 name。项目原则草稿由 `principle-maintenance` 管理；CLI 接受任意位置及文件名。草稿采用上面的 description 头，正文为非空 UTF-8 文本；引用和附件按正式位置安排。CLI 保留原始字节与源草稿，不保存审批状态。

```powershell
handbook import-principle docs/research/principle-drafts/design/use-evidence.md --scope design --name use-evidence
handbook load project:principle:design/use-evidence
```

命令将正文写入当前项目根下的 `docs/knowledge/principles/design/use-evidence/PRINCIPLE.md`，自动创建或补充 `docs/resources.json`。已有有效字段和资源根保留。`FILE` 的相对路径从项目根解析，也可传入已审定草稿的绝对路径。默认同名冲突返回错误，审定修订稿后以 `--replace` 更新已有目标；替换缺失目标和源目标相同也返回错误。

输入、声明与目标冲突在写入前失败。普通写入失败及写入后的发现失败返回 `ok: false`，并用 `error.current` 报告声明与正文的实际写入结果；先核对这些结果，再修复原因和重试。完整错误分类及恢复方式见协议的“入库错误与恢复”。首次成功后可直接通过 scopes、list、load 和 validate 消费该原则。
