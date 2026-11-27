# Handbook

`handbook` 提供 workbook 与 principle 的目录、正文加载和声明校验，并将已审定原则草稿写入项目正式库。Skill 使用宿主发现入口。

## 命令

| 命令 | 参数与结果 |
| --- | --- |
| `scopes` | 可选 `--kind workbook\|principle`。`scopes[]` 返回当前项目可见资料的目录分类，去重并排序。 |
| `list` | 可选 `--kind workbook\|principle` 和可重复的 `--scope SCOPE`。多个分类取并集；省略时不按分类筛选。`resources[]` 每项严格只有 `resourceId` 和 `description`，两类资源一致。 |
| `load ID [ID ...]` | 接受一个或多个完整 ID 或唯一短名，共用一次项目解析与资料目录。返回入口及 workbook 递归 includes 的正文与来源，批量响应见下文。 |
| `validate` | 校验 principle 两级布局、入口头信息、身份和 includes 引用，返回 checkedSources 与 resourceIds。 |
| `import-principle FILE --scope SCOPE --name NAME [--replace]` | 将已审定草稿入库。返回 `resourceId`、绝对 `entryPath` 和 `operation`（`created` 或 `updated`）。 |

scopes、list、load 和 validate 从目标项目根运行，读取该根的项目资料和全局 core Skill 的资料目录。principle 的 scope 取 principles 下一级目录的完整名称，`programming-workflow` 与 `programming-design-architecture` 平级且精确匹配。workbook 的 scope 取入口父目录名中第一个连字符前的部分，无连字符时取完整目录名。workbook 的 includes 可跨分类加载。

可在任意目录用 `-h` 或 `--help` 查询参数，用 `-v` 或 `--version` 查看版本。帮助为纯文本，业务结果为精简 JSON。

### 原则入库

`import-principle` 从目标项目根运行。`FILE` 从当前根解析，也接受已审定草稿的绝对路径。输出始终位于当前根。scope 和 name 使用现有英文小写连字符 token 规则。

正式入口为 `docs/knowledge/principles/<scope>/<name>/PRINCIPLE.md`，身份为 `project:principle:<scope>/<name>`。默认只创建新目标，已有目标返回冲突。`--replace` 只更新已有文件，目标缺失时报错。源文件与目标指向同一文件时拒绝入库。

输入接受任意文件名，按 principle schema 校验 YAML 头，正文应为非空 UTF-8 文本。头信息只接受 description，不增加审批、scope 或 name 字段。CLI 保留已审定文件的字节和源草稿，不改写语义，也不搬运附件。正文及目标身份的用户审定、正式引用和附件位置由调用工作流确认。

入库先校验输入、目标和已有项目声明，再写入声明与正文，最后用既有项目来源及资料目录验证正式身份可发现。成功响应为 `{"ok": true, "resourceId": "project:principle:<scope>/<name>", "entryPath": "<绝对路径>", "operation": "created"}`，替换时 operation 为 updated，退出码为 0。

### 项目资源声明

handbook 内部模块统一创建、合并和校验 `docs/resources.json`。调用方提供当前项目根及相对 docs 的资源根，原则入库请求 `knowledge/principles`。

缺少声明时，模块创建 schemaVersion 为 1、source 为 project、version 为 1.0.0、install 为空数组的声明文件，resourceRoots 包含请求的资源根。已有声明按 resourceManifest schema 和既有路径规则校验，保留有效字段、版本、安装声明及资源根，再补充缺项并去重。已有父级根覆盖请求路径时，不新增重叠根。请求的父级根会覆盖既有子级根时，预检返回 resource_conflict，保留既有声明；调用方先明确整理声明再重试。声明未变化时不写文件。有效自定义根保留，原则仍写入标准路径。

模块准备阶段不创建目录或文件。格式损坏、source 非 project、非法资源根或越界路径在写入前报错，并保留原声明。模块只维护通用资源声明，不处理原则正文与身份。

### 入库错误与恢复

失败响应沿用 `ok: false`、`error.code` 和 `error.message`，退出码为 1。有定位信息时返回 `error.conflicts`。

| code | 入库条件 |
| --- | --- |
| `invalid_arguments` | 非法 scope/name、源文件与目标相同，或参数组合无效。 |
| `invalid_reference` | 源文件缺失或不是文件、替换目标缺失，或资源来源无法读取。 |
| `invalid_schema` | 草稿头信息或正文格式无效、Package 不符合 schema。 |
| `invalid_json` | Package JSON 损坏或包含重复键。 |
| `identity_conflict` | 已有清单的 source 不是 project。 |
| `path_outside_root` | 声明、资源根或正式目标越过项目路径边界，或路径组成无效。 |
| `resource_conflict` | 创建目标已存在、既有资源根彼此重叠、请求资源根与既有子级根重叠，或发现链遇到重复身份、重复物理入口。 |
| `io_error` | 读取、目录创建或文件发布时发生普通 I/O 错误。 |

输入、声明与目标冲突在修改前返回。文件分别复用既有原子发布能力；声明与正文不组成跨文件事务。先写声明，再写正文。普通 I/O 失败和写入后的发现失败保留已经发布的结果，不报告成功，也不自动回退已发布文件。

写入阶段失败时，`error.current` 返回绝对 `packagePath`、`entryPath`，以及 `packageWritten`、`entryWritten`。标记为 true 表示已确认该文件包含本次待写内容；false 表示未发布该文件；无法确认时为 null。声明无需变更时，packageWritten 为 false。仅调用模块时，错误包含该模块负责的 packagePath 和 packageWritten。错误码保留实际失败分类。

恢复时先核对 error.current 指向的文件。正文未发布时，保留草稿，修复失败原因后重试原创建或替换操作。正文已发布或状态无法确认时，先核对正文与声明，再决定是否用 `--replace` 重试或修复发现错误。未确认当前结果前，不把失败当作未写入。

### 批量加载与错误

成功响应包含 `ok: true`、`selectedIds[]` 和 `resources[]`。`selectedIds` 保存解析后的完整入口 ID，按输入顺序去重。恰好传入一个 ID 时，响应还保留原 `selected` 字符串；传入多个参数时省略该字段，即使参数指向同一入口。

`resources` 按完整 ID 全局去重，保留首次遍历顺序；workbook 的依赖先于引用者返回。重复入口、短名与完整 ID 指向同一入口、多根共享依赖均只读取并输出一份正文。每项包含 `resourceId`、`kind`、`name`、`description`、`source`、`entryPath` 与 `content`；workbook 有非空 includes 时保留 `includes`。principle 的 `name` 取二级目录名。

任一入口缺失或歧义、格式非法或 includes 无效时，整次响应为 `ok: false`，退出码为 1，不返回部分成功正文。`error.code` 与 `error.message` 保留原分类及定位信息。短名歧义返回 `resource_conflict`，消息标明出错输入，`error.conflicts[]` 按完整 ID 排序给出全部候选，可直接用于下一次加载。有其他冲突定位信息时，同一字段返回原定位对象。正文中的普通引用按条件读取。

## 作者格式

principle 使用 `principles/<scope>/<principle>/PRINCIPLE.md`，相对于来源内的 principles 根固定两级目录。scope 和 principle 使用英文小写连字符名称；scope 不按连字符分层。资源来源与目录派生 `<source>:principle:<scope>/<principle>`，YAML 头只接受 `description`。`includes` 即使为空也在目录发现阶段返回 `invalid_schema`。改动 scope 或原则目录名后同步当前身份与路径引用；中文标题和 description 不影响身份。

workbook 的入口目录仍为 `<scope>` 或 `<scope>-<topic>`。`WORKBOOK.md` 的 YAML 头包含 `name`、`description` 和按需 `includes`；已被引用的 `resourceId` 保留，省略时使用 `<source>:workbook:<目录名>`。workbook 可递归包含 workbook 与 principle；principle 为叶子，单条加载只返回自身。

完整 ID 精确加载；principle 短名为 `scope/principle`，workbook 短名为 ID 最后一段，均只在当前目录中唯一时可用。重复身份、短名歧义、缺失 includes 和 workbook 依赖环返回错误。校验不限制正文篇幅。

入口类型取自文件名。正文头与资源清单的结构由 `guides.schema.json` 定义。正文头只接受 schema 声明的键。

## 资源清单与安装

core 从所选 agent 的全局 `principles` 和 `workbook` 各自读取资料。所有命令支持 `--agent`，省略时沿用项目安装记录或默认 `codex`。core 源码的 `skills/resources.json` 用于仓库校验。

扩展声明在 `.agents/extensions/<extension>/extension.json`，保存扩展名、版本、资源根、安装映射及可选的成果和关系类型。handbook 按项目安装记录发现受管资料，保留 workbook 与 principle 的稳定身份和相对引用。上游 Skill 更新后，通过 [harness-install](../installation/PROTOCOL.md) 显式更新项目快照。

项目自有资料由 `docs/resources.json` 声明，其路径与版本由项目维护。
