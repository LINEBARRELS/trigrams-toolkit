# Project State

Project State 登记 Module、Feature 和正式文稿的身份、归属与额外关系。Plan 和 Task 的状态由 Plan 工具维护。

## 命令

| 命令 | 用途 |
| --- | --- |
| `register module NAME [--id ID]` | 新建 Module，或按 ID 更新名称 |
| `register feature NAME [--module MODULE_ID] [--id ID]` | 新建或更新 Feature；新建时提供 Module，更新时可沿用归属 |
| `register artifact PATH [--kind TYPE] [--module MODULE_ID] [--feature FEATURE_ID]...` | 读取文稿身份与标题，根据参数维护归属、文件头和索引 |
| `locate ID` | 只返回目标的公共视图；Artifact 附加实际绝对路径 |
| `list [--kind TYPE]` | 列出基础公共视图，不解析路径；可按 module、feature、artifact 或完整类型筛选 |
| `related ID [--direction DIRECTION]` | 返回一跳邻居与关系；Artifact 邻居附加路径；方向默认为 both，也可选 incoming、outgoing |
| `relate FROM RELATION TO [--remove]` | 增删已声明的额外关系；RELATION 是关系类型名 |
| `validate` | 检查身份、文件头与索引的归属一致性及关系；索引不存在时也可运行 |

在目标项目根执行命令。`-h`／`--help` 和 `-v`／`--version` 可在任意目录查看。帮助为纯文本，业务结果为 `{ "ok": true, "data": ... }`，错误为 `{ "ok": false, "error": { "code": ..., "message": ... } }`。成功退出码为 0，失败为 1。

相对路径从当前目录解析，项目根与文稿边界按真实路径判断。Windows 短路径和目录链接沿用真实目录的身份。Windows 路径比较忽略大小写，Linux 路径比较区分大小写。每个 Git worktree 使用自身的项目根和索引。

新 Module、Feature 省略 `--id` 时，工具分别生成 `module_`、`feature_` 加 10 位随机后缀的 ID，返回于 `data.entity.id`。名称是独立字段，同名登记不会自动复用身份。若上次创建的结果不确定，先用 `list` 核对。调用方可以提供符合格式的稳定 `--id`；更新已有节点时传入原 ID，Feature 省略 `--module` 会沿用原归属。这两个命令只维护索引，调用方负责将 ID 回填到 ARD 节点，并同步节点名称与树位置。

## 查询与资料导航

`locate` 的 `data` 直接包含目标字段。Module 返回 `id/kind/name`，Feature 另有 `moduleId`。Artifact 返回 `id/kind/title/featureIds/path`，有 Module 归属时另有 `moduleId`。无 Feature 归属时，`featureIds` 为空数组。清单型 Artifact 的 `path` 指向清单文件。

`related` 的 `data` 只包含 `items` 和 `relations`。`items` 使用与 `locate` 相同的公共字段，每个邻居只出现一次；`relations` 保留匹配边的 `kind/from/to/source`。查询只遍历一条边，先按方向筛选，再定位邻接文稿。Feature 的 Module 是直接邻居，Module 的其他文稿不自动进入结果。

查询模块资料时，运行 `project-state related <Module ID>`，读取 `data.items` 中 Artifact 的 `path`。从 Feature 导航时，可用 `locate <Feature ID>` 的 `data.moduleId`，或 `related <Feature ID>` 返回的 Module，再主动查询模块。每次调用检查退出码为 0 和 `ok: true`。

`list` 保留 `data.items`、类型筛选和按 ID 排序，每项采用基础公共字段，不返回 `path`。失联文稿仍可枚举。`locate` 与 `related` 的目标未登记或本次应定位的正文缺失时返回 `invalid_reference`，正文身份重复时返回 `identity_conflict`，整体查询失败。无关文稿和方向筛选掉的文稿失联不影响查询。

本次查询输出有破坏性变化：删除旧 `entity/message/specs/viaModule` 包装，停止 Feature 自动展开 Module 文稿。三个查询均不再返回内部 `locatorHint/identityMode`。注册返回契约不变；`plan-toolkit inspect` 的 `data.specs` 仍表示 Task 的正式输入。

## 文稿登记

调度 Agent 通过命令参数提交正式文稿的归属。文稿作者保留已有身份，交付路径与归属信息，不必预填 YAML 头：

```powershell
project-state register artifact docs/inventory.md --kind core:architecture-spec --module module_inventory --feature feature_slots --feature feature_sorting
```

`--feature` 可重复使用，每次传入一个 Feature ID，并要求同次提供 `--module`。CLI 校验节点存在、Feature 属于该 Module 且列表不重复，然后统一写回文件头与索引：

```yaml
---
artifact-id: artifact_inventory
moduleId: module_inventory
featureIds: [feature_slots, feature_sorting]
---
# Inventory Spec
```

`artifact-id` 缺失时，登记会生成并写入身份。Artifact ID 使用 `artifact_` 前缀，示例中的可读 ID 代表已有身份；自动生成的 ID 使用 10 位随机后缀。重复登记复用 YAML 头中的身份。标题优先读取 `title`，其次读取首个一级标题，最后使用文件名。

首次登记不传归属参数时，文稿无归属。已登记文稿不传归属参数时，沿用索引中已接受的归属。传入 `--module` 时，用该 Module 和本次全部 `--feature` 替换原归属；只传 `--module` 就清空 Feature 列表。

`artifact-id`、`moduleId`、`featureIds` 由工具维护。手改头部不会改变登记归属；`validate` 会报告与索引不符的归属，重新登记会按已有索引或本次参数恢复头部。其他头部字段、注释与文稿内容保留，头部由 YAML 解析器序列化，排版可随之调整。归属关联由索引展开，`relate` 不重复维护这组关联。

Artifact 的 `kind` 表示文稿类型，只保存在索引，不写入 YAML 头。登记专门类型时显式传入 `--kind`；Implementation Spec 使用 `core:architecture-spec`，其他 core 类型见 [Artifact 类型契约](PROTOCOL.md#artifact-类型)。省略时沿用已登记类型，首次登记使用 `core:document`；CLI 不根据文稿内容推断类型。已有文稿可用原路径和 `--kind` 更新类型，省略归属参数即可保留原归属。

核心类型与额外关系随 Python 包发布。扩展类型通过项目安装记录读取快照声明，项目类型继续来自 `docs/resources.json`。

二进制成果可使用带 `schemaVersion: 1`、`id`、`members` 的身份清单登记。相同归属参数写入清单的 `moduleId`、`featureIds`，成员路径相对于项目根。正文定位按身份扫描 `docs/` 和 `plans/`，跳过 `docs/archives/` 的自动扫描，并检查索引中已有的路径提示。移动正文后，在扫描范围内仍可定位。

## 额外关系

`relate FROM RELATION TO [--remove]` 的 RELATION 是关系类型，与文稿的 `--kind` 不同。例如 `relate artifact_new core:supersedes artifact_old` 表示前者取代后者；两端应为同类型 Artifact。项目或扩展还可声明额外关系类型。`--remove` 只删除关系，不修改文稿。Feature 的 Module 归属通过 `register feature --module` 维护，文稿归属通过 `register artifact --module --feature` 维护。

## 存储

索引的 `schemaVersion` 固定为 `1`，保存在项目根的 `.project-state/state.json`。内容只有 Module、Feature、Artifact 和额外关系。写入使用文件锁与同目录原子替换，锁冲突直接报错。登记先验证身份与归属，再写文件头，最后写索引。两份文件不构成原子事务。索引失败后以相同归属参数重跑，仍复用同一身份。仅修复文件头时，结果中的 `changed` 也为 `true`。

格式不符时，命令返回 `invalid_schema`。先归档原状态，再按 `project-setup` workbook 重新登记。

## 开发与验证

Project State 与其余三个 CLI 共用 Python 3.11+ 包、依赖和版本。安装可编辑包后，在仓库根执行：

```sh
python -m mypy
python -m unittest discover -s tests -p 'test_project_*.py' -v
python tasks.py build
python tasks.py verify-package
```

测试使用 `.tmp/` 的隔离项目，覆盖身份、归属、查询、文稿保真、关系、锁和 Git worktree。平台回归覆盖含中文与空格的路径、真实路径、目录链接、Windows 短路径与 Linux 大小写。包验收从隔离项目根调用标准入口，回执写入指定 output。
