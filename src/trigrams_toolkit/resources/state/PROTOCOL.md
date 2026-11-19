# Project State 协议

公开入口由 [commands.json](commands.json) 声明，共 8 个叶子命令。调用方传入位置参数与选项。业务返回 JSON，帮助返回纯文本。具体签名与默认值见 [README](README.md)。

## 项目根

项目根为进程当前工作目录的真实路径。调用方在目标项目根运行命令，相对路径以该根解析。每个 Git worktree 使用自身根目录下的 `.project-state/state.json`。超出项目边界的真实路径返回 `path_outside_root`。Windows 比较忽略大小写，Linux 比较区分大小写。`-h`／`--help` 和 `-v`／`--version` 可在任意目录查看。

## 架构索引

[架构索引](state.schema.json) 只保存 Module、Feature、Artifact 与额外关系，`schemaVersion` 固定为 `1`。实体 ID 保持稳定。Artifact 使用 `artifact_` 前缀，CLI 在 YAML 头维护 `artifact-id`，缺失时生成；已有身份保持不变。

`register artifact PATH [--kind TYPE] [--module MODULE_ID] [--feature FEATURE_ID]...` 接收归属参数。`--feature` 可重复，要求同次提供 `--module`。提供 Module 时用本次全部 Feature 替换原列表；不传归属参数时沿用索引，首次登记则无归属。头部归属不作为登记输入。工具验证节点存在及 Feature 的树归属，统一写回 `artifact-id`、`moduleId`、`featureIds`；清单模式使用 `id` 身份字段并维护相同归属字段。

`relate FROM RELATION TO [--remove]` 维护已声明的额外关系，检查端点类型、基数和环路。RELATION 是关系类型，如 `core:supersedes`，输入契约和存储字段仍名为 `kind`。归属关系从登记参数产生，不能另用 `relate` 维护。相同关系增删按当前状态收敛。

## 公共查询视图

`locate`、`related`、`list` 从 Registry 显式投影公共字段，不直接返回内部实体。基础视图如下：

| 实体 | 字段 |
| --- | --- |
| Module | `id`、`kind: core:module`、`name` |
| Feature | `id`、`kind: core:feature`、`name`、`moduleId` |
| Artifact | `id`、`kind`、`title`、可选 `moduleId`、`featureIds` |

Artifact 无 Module 归属时省略 `moduleId`，无 Feature 归属时返回 `featureIds: []`。`name` 与 `title` 沿用各实体的名称字段。查询不返回 `locatorHint`、`identityMode`、`entity`、`message`、`specs` 或 `viaModule`。注册命令仍沿用原返回契约，内部索引字段与 schema 不变。

### 单实体定位

`locate ID` 的 `data` 直接承载目标视图。Module、Feature 只返回基础字段，不返回 `path`。Artifact 在基础字段上附加按身份定位得到的绝对 `path`；清单型 Artifact 的 `path` 指向清单文件。

定位按身份扫描项目根下的 `docs/`、`plans/` 以及已登记的路径提示。默认扫描跳过 `docs/archives/`，明确登记的路径提示仍可定位。正文移动后，处于扫描范围内即可通过身份查找。`locate` 不查询关联文稿，也不沿 Feature 的 `moduleId` 展开 Module 文稿。无关文稿或邻接文稿失联不影响本次单实体定位。

### 一跳关联查询

`related ID [--direction DIRECTION]` 的 `data` 只包含 `items` 和 `relations`。`items` 使用 `locate` 的实体视图，Artifact 附加实际绝对 `path`。每个邻接实体 ID 只出现一次，目标自身不进入 `items`。`relations` 保留所有匹配关系，同一对端点之间的不同关系不合并。

直接关联取自登记产生的归属关系和显式额外关系。每条关系包含 `kind/from/to/source`，方向只按 `from/to` 判断：

| 关系 | 方向 | `source` |
| --- | --- | --- |
| `core:feature-module` | Feature → Module | `feature` |
| `core:module-spec` | Module → 声明该 `moduleId` 的 Artifact | `document` |
| `core:feature-spec` | Feature → `featureIds` 含该 Feature 的 Artifact | `document` |
| 显式额外关系 | 登记的 `from` → `to` | `relation` |

`direction` 默认为 `both`。`outgoing` 只保留 `from` 为目标 ID 的边，`incoming` 只保留 `to` 为目标 ID 的边，`both` 保留两者。查询先筛选关系，再定位邻接 Artifact，只遍历一条边。无关文稿或方向筛选掉的文稿不触发定位错误。

Feature 的 Module 是直接邻居，Module 的其他文稿不因此进入结果。Module 直接关联所有声明该 `moduleId` 的 Artifact，包括同时归属于 Feature 的文稿。跨 Module 的显式关系按实际端点返回。无邻居时返回 `items: []` 与 `relations: []`。

查询模块文稿时，运行 `related <Module ID>`，读取 `data.items` 中 Artifact 的 `path`。从 Feature 导航模块资料时，先读取 `locate <Feature ID>` 的 `data.moduleId`，或读取 `related <Feature ID>` 中的 Module，再主动查询该 Module。

### 枚举与失败语义

`list [--kind TYPE]` 保留 `data.items`、既有类型筛选及按 ID 的排序规则。每项只使用基础视图，不解析或返回 `path`。失联文稿仍可枚举，实际路径通过 `locate` 获取。

`locate` 与 `related` 的目标未注册时返回 `invalid_reference`。本次应返回路径的 Artifact 无身份正文时返回 `invalid_reference`，多份正文声明同一身份时返回 `identity_conflict`。定位失败沿用现有错误信封，整体查询失败，不返回部分成功结果。路径边界、索引读取与 IO 错误继续透传。

三类查询的输出分别由 [cli.schema.json](cli.schema.json) 的 `locateResponse`、`relatedResponse`、`listResponse` 约束。[commands.json](commands.json) 引用对应定义；其他命令保留既有信封契约。

本次查询输出为破坏性变更，不保留旧字段别名。`plan-toolkit inspect` 的 `data.specs` 仍表示 Task 正式输入，继续逐项接收 `locate` 的路径或错误。

## Artifact 类型

Artifact 的类型使用 Registry 中的 `kind` 字段，登记时通过 `--kind` 指定。core 类型名称由 [core-types.json](core-types.json) 声明，语义如下：

| `kind` | 用途 |
| --- | --- |
| `core:document` | 通用文档，适用于未采用专门类型的文稿 |
| `core:architecture-spec` | Module 的实现设计与契约，即 Implementation Spec，定义所属 Feature 的行为、接口、状态和运行约束 |
| `core:code-architecture` | 整体代码架构与工程组织文档，如 DEVTECH、ARD，定义技术栈、架构分层、Module / Feature 边界和依赖方向 |
| `core:review` | 交付审核报告，记录审核结论、问题与验证证据 |

调用方登记上述专门类型的文稿时，应显式传入对应的 `--kind`，并在交接待登记信息时提供该类型。CLI 不根据文件名、目录、标题或正文推断类型。省略 `--kind` 时，已登记 Artifact 沿用原类型，首次登记使用 `core:document`。显式传入 `--kind` 可更新已有 Artifact 的类型，身份保持不变。

`kind` 只保存在 Registry，不写入 YAML 头。类型用于 `list --kind` 筛选及额外关系的端点校验。`locate` 按 ID 定位，`related` 按直接关系查询，两者都不按 `core:architecture-spec` 限制 Artifact 类型。

## 写入

写入持有索引文件锁，用同目录临时文件原子替换。校验失败不改写文稿或索引。文件头先于索引落盘，两次写入不是跨文件原子事务；若索引写入失败，以相同参数重试会复用已有身份。仅文件头修复也返回 `changed: true`。新节点创建的结果不确定时，调用方先查询已有节点。

格式不符时，命令返回 `invalid_schema`。调用方先归档原状态，再按 `initialize` workbook 重新登记。

CLI 的输入与响应目录见 [cli.schema.json](cli.schema.json)。这些 schema 用于本地契约验证。
