# Trigrams toolkit

## 项目概况

本仓库维护跨领域的 Agent 工具包 Trigrams toolkit，采用 Vercel skills 分发、统一 Python CLI 包与项目级扩展快照装配。Skill 负责行为，workbook 定义工作方法，principle 提供判断标准；Plan 组织交接与执行。

## 开发文档

| 文档 | 固定路径 | 用途与读取时机 |
| --- | --- | --- |
| 开发与接入 | [docs/getting-started.md](docs/getting-started.md) | 开发环境准备、源码校验与目标项目三段接入流程；搭建环境或核对接入方式时读取 |
| 维护与发布 | [docs/maintenance.md](docs/maintenance.md) | 唯一维护源、定向验证矩阵、CI 与标签发布步骤；修改维护源或发布版本时读取 |


| 路径 | 用途与读取时机 |
| --- | --- |
| `docs/plans/` | Plan仓库 |

对于项目架构或工作流程理解有疑问可以使用全局安装的 `toolkit-steward` skill 进行咨询。

## 工程目录

下列路径相对仓库根目录，均为本工具包的唯一维护源或配套验证入口：

| 路径 | 职责 |
| --- | --- |
| `skills/` | 通用 core Skill 唯一维护源；核心 workbook 与 principle 随对应 Skill 维护 |
| `extensions/` | 官方扩展唯一维护源（`extensions/game/`、`extensions/toolkit-maintenance/`）；各扩展通过 `skills/extension-setup-<extension>/assets/` 维护自身的 `extension.json`、`principles/` 与 `workbooks/` |
| `src/trigrams_toolkit/` | 统一 Python CLI 包源码（`project-state`、`plan-toolkit`、`handbook`、`harness-install`）；协议与核心类型随 `src/trigrams_toolkit/resources/` 交付 |
| `scripts/` | 仓库只读校验与发行包验收脚本（`verify_toolkit.py`、`check_protocols.py`、`check_package.py`） |
| `tests/` | 单元测试、运行时测试（`tests/runtime/`）与多工具源码验收测试 |
| `tasks.py`、`toolkit.json` | 跨平台检查、测试、构建与发布统一入口，以及源码仓清单 |

## 开发与验证

以下命令均在仓库根目录运行。完整开发、CI 与标签发布流程见[开发与接入](docs/getting-started.md)和[维护与发布](docs/maintenance.md)。

| 命令 | 用途 | 前提与验证状态 |
| --- | --- | --- |
| `handbook validate` | 校验全局 core 与当前项目已装配扩展资源 | 已验证 |
| `PYTHONPATH=src python scripts/verify_toolkit.py` | 校验仓库源码资料、Skill 元数据与本地链接 | 已验证（无需安装 editable 包） |
| `PYTHONPATH=src python scripts/check_protocols.py` | 校验命令声明与 JSON Schema 引用闭包 | 已验证（无需安装 editable 包） |

## 项目约束

- 不应修改非当前任务所属或已完成（`done`）的历史 Plan、Task、交付证据与审核记录。
- 历史 Plan 内的旧引用、旧签名与当时快照属于历史审计证据，不应逆向同步。
- 修改维护源时，应同步更新实际调用方、协议契约与文档说明，并运行 `python tasks.py check` 及对应范围测试。
- 打包、隔离验收与发布统一使用根目录 [tasks.py](tasks.py)。
- 代码开发时，应按任务和语言查阅[现有原则目录](skills/principles/principles)中的相关 `PRINCIPLE.md`，用于设计、实现与审查。
- 临时文件、过程日志与调试输出应放在项目根 `.tmp/`。

### 项目术语

- **core 资料**：随全局 `principles`、`workbook` Skill 分发的通用原则与工作方法，资源 ID 前缀为 `core:`。
- **扩展快照（extension snapshot）**：由 `harness-install` 固化到目标项目 `.agents/extensions/<extension>/` 的扩展清单、原则与工作方法副本。

### 公共工具与项目配置

四个公共 CLI 的帮助（`-h`）可在任意层级查看。

| 命令 | 用途 |
| --- | --- |
| `handbook` | workbook 与 principle 的发现和加载 |
| `project-state` | 项目内架构实体、成果与关系的登记和查询 |
| `plan-toolkit` | plan（仅Flow 模式）的读取、依赖检查与当前状态 |
| `harness-install` | 项目资源装配、全局 Skill 补齐与旧运行状态归档 |
