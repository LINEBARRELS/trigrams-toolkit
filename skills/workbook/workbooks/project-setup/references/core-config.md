# 基础配置与资源核对

本说明对应[主 workbook](../WORKBOOK.md#原子工作目录)的**工作 1（基础配置与资源核对）**，并维护工作 1 与工作 4 共用的 `harness-install` 装配门禁。全局 CLI 与 core Skill 的安装和恢复见 `toolkit-steward`。

## 材料归属与边界

| 组件 | 维护与安装方式 | 项目内位置与说明 |
| --- | --- | --- |
| 项目安装记录 | `harness-install` 维护 | `.agents/harness.json`；记录目标 `agent`、已启用扩展与受管文件基线 |
| 外部必需 Skill | `harness-install install apply` 补齐 `answer-me-with-html` 与 `smell-check` | 目标 `agent` 的全局 Skill 目录 |
| 扩展 Skill 与快照 | 见[扩展管理](extensions.md) | `.agents/skills/`（Claude Code 为 `.claude/skills/`）与 `.agents/extensions/<extension>/` |
| 项目自有资料 | 项目自行维护 | `docs/resources.json` 不纳入 `.agents/harness.json` |

调用 `harness-install` 时，通过 `agent` 指定 Vercel skills 宿主（单选：`codex`、`claude-code`、`pi`；省略时沿用已有记录或默认 `codex`）。详细字段通过 `harness-install install preview --help`、`apply --help` 与 `--help schema` 查询。

## 执行步骤

1. **旧运行状态归档（按需）**：若存在退役的 `.agents/harness.yaml`、`.agents/harness-lock.json` 或不兼容的旧 `.agents/harness.json`，先停止相关写入并向用户确认项目内相对路径，运行 `harness-install archive PATH...` 移入 `.harness-archive/<批次>/`。
2. **核对并收敛 `.agents/harness.json`**：
   - 检查现有 `.agents/harness.json` 中的 `agent` 与 `extensions` 是否正确；缺失、需修复或存在旧版受管角色入口待清理时，执行下方统一装配门禁（首次纯核心装配传入 `extensions: []`；已有正常扩展配置时保留原 `extensions` 列表）。
3. **合并根忽略文件（按需）**：将 [.gitignore](../assets/templates/.gitignore)、[.ignore](../assets/templates/.ignore) 与 [.rgignore](../assets/templates/.rgignore) 置入项目根；已有对应文件时增量合并规则，不覆盖项目既有条目。
4. **核对项目资源配置（`docs/resources.json` 与已装配资源）**：
   - 若项目已有 `docs/resources.json` 或自建 `docs/workbooks/`、`docs/knowledge/principles/`，核对其声明为 `project` 来源且 `resourceRoots` 与实际目录一致；项目尚无自建 workbook 或 principle 时，不必创建空 `docs/resources.json`。
   - 项目 principle 应经 `principle-maintenance` 提炼并在用户审定后由 `handbook import-principle` 入库，CLI 自动维护原则资源声明。
   - 在项目根运行 `handbook validate`，确认 core、已装配的 `.agents/extensions/` 资源与项目自建资源均通过校验。

## 统一装配门禁（preview → apply）

工作 1 与工作 4 的所有 `.agents/harness.json` 与扩展快照写入均遵循同一两步门禁：

1. **预览装配并说明影响**：将 `agent` 与 `extensions` 写入输入，运行 `harness-install install preview --input <输入文件>`（只读，可离线运行）。审阅变更、冲突与 `projectRoot`，向用户说明项目内将写入或移除的受管路径、目标 `agent`，以及 `apply` 可能写入目标 `agent` 全局 Skill 目录以补齐缺失的 `answer-me-with-html`、`smell-check`。出现本地修改或同名冲突时，先确认保留或归档策略并重新预览。
2. **应用装配**：取得确认后运行 `harness-install install apply --input <确认文件> --request-id <请求ID> --expected-revision <baseRevision>`（确认文件包含原样 `preview` 与 `confirmedBy`）。全局依赖补齐失败时，按返回的 Skill 与 agent 排查环境后重试。
