# Harness 装配与扩展管理

本说明对应[主 workbook](../WORKBOOK.md#原子工作目录)的**工作 1（基础配置与资源核对）**与**工作 2（扩展管理）**。全局 CLI 与 core Skill 的安装和恢复见 `toolkit-steward`。

## 材料归属与边界

| 组件 | 维护与安装方式 | 项目内位置与说明 |
| --- | --- | --- |
| 扩展 Skill | Vercel skills 安装到项目 | 通用目录为 `.agents/skills/`，Claude Code 为 `.claude/skills/`（`skills-lock.json` 由 Vercel 管理） |
| 外部必需 Skill | `harness-install install apply` 补齐 `archify` 与 `smell-check` | 目标 `agent` 的全局 Skill 目录 |
| 扩展资源快照 | `harness-install` 从 `extension-setup-<extension>/assets/` 复制 | `.agents/extensions/<extension>/`（`extension.json`、`principles/`、`workbooks/` 及相对配套文件） |
| 平台角色 adapter | `harness-install` 从统一 Python CLI 包复制 | `.codex/agents/`、`.claude/agents/` 或 `.pi/agents/`；`platforms` 支持 `codex`、`claude`、`pi-web`（与 `agent` 独立选择） |
| 声明附加材料 | `assets/extension.json` 的 `install` 字段声明 | 按声明的 `target` 与交集 `platforms` 复制并受文件基线保护 |
| 项目自有资料 | 项目自行维护 | `docs/resources.json` 不纳入 `.agents/harness.json` |

调用 `harness-install` 时，目标平台包含两类参数：Vercel skills 的 `agent`（单选：`codex`、`claude-code`、`pi`）与宿主 adapter 的 `platforms`（多选：`codex`、`claude`、`pi-web`）。详细字段通过 `harness-install install preview --help`、`apply --help` 与 `--help schema` 查询。

`extensions` 传入本次期望保留的**完整扩展集合**（省略时沿用已有选择，传入 `[]` 清空全部扩展）。上游扩展 Skill 更新后，在显式运行 `harness-install` 同步前，`handbook` 与 `project-state` 继续读取既有快照。开发调试或旧来源缺失时，可通过绝对路径 `packages` 指定来源根。

## 工作 1：基础配置与资源核对

1. **旧运行状态归档（按需）**：若存在退役的 `.agents/harness.yaml`、`.agents/harness-lock.json` 或不兼容的旧 `.agents/harness.json`，先停止相关写入并向用户确认项目内相对路径，运行 `harness-install archive PATH...` 移入 `.harness-archive/<批次>/`。
2. **核对并收敛 `.agents/harness.json` 与 adapter**：
   - 检查现有 `.agents/harness.json` 中的 `agent`、`extensions` 与 `platforms` 是否与当前需求一致；缺失或需修复时，执行下文统一装配步骤（无扩展时传入 `extensions: []`）。
   - Pi Web 入口开启 `load_skills` 并继承父会话模型；使用前应在宿主启用内置子代理并确认全局 core Skill 可见。
3. **合并根忽略文件（按需）**：按需将 [.gitignore](../assets/templates/.gitignore)、[.ignore](../assets/templates/.ignore) 与 [.rgignore](../assets/templates/.rgignore) 置入项目根；已有对应文件时增量合并规则，不覆盖既有项目规则。
4. **核对项目资源配置（`docs/resources.json` 与扩展资源）**：
   - 若项目已有 `docs/resources.json` 或自建 `docs/workbooks/`、`docs/knowledge/principles/`，核对其声明为 `project` 来源且 `resourceRoots` 与实际目录一致；项目尚无自建 workbook 或 principle 时，不必创建空 `docs/resources.json`。
   - 项目 principle 应由 `principle-maintenance` 提炼草稿并在用户审定后通过 `handbook import-principle` 入库，CLI 会自动维护项目原则资源声明。
   - 在项目根运行 `handbook validate`，确认 core、已装配的 `.agents/extensions/<extension>/` 与项目自建资源均能正常发现并通过校验。

## 工作 2：扩展安装、增补、同步与移除

`extension-setup-<extension>` 设为仅手动触发（`disable-model-invocation: true`），避免常驻日常开发上下文。执行工作 2 时，由当前 Agent 直接按项目路径读取该 Skill 正文：

- 通用路径：`.agents/skills/extension-setup-<extension>/SKILL.md`
- Claude Code：同步检查 `.claude/skills/extension-setup-<extension>/SKILL.md`

### 安装或增补扩展

1. **确认当前 `agent` 与既有扩展**：已接入项目查看 `.agents/harness.json` 中的 `agent`、`extensions` 与 `platforms`，增补时沿用同一 `agent`。
2. **安装目标扩展 Skill**：在项目根目录运行：
   ```sh
   npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*'
   ```
   使用 Claude Code 时附加 `-a claude-code`；第三方扩展替换为对应来源。确认项目 Skill 目录中已出现 `extension-setup-<extension>/SKILL.md` 且无异源同名冲突。
3. **装配快照**：构造包含**既有扩展与新增扩展完整列表**的输入，执行下方统一装配步骤。
4. **按路径读取 setup 约定**：直接读取项目 Skill 目录下的 `extension-setup-<extension>/SKILL.md` 及正文引用的配套说明，获取领域目录、文档与术语导航增量，交由工作 3、工作 4 落地（仅增补扩展时，直接增量补齐目录并更新 `AGENTS.md`）。

### 上游同步与移除扩展

- **显式同步快照**：先通过 Vercel skills 更新项目扩展 Skill，再用保留当前集合（或省略 `extensions`）的输入执行统一装配步骤，核对本地修改冲突后刷新 `.agents/extensions/<extension>/`。
- **移除扩展**：从 `extensions` 列表中移除目标扩展名（传 `[]` 清空全部扩展），执行统一装配步骤卸载受管快照与安装声明（保留项目自有文稿、正式成果、Plan 与本地修改），随后在 `AGENTS.md` 中删除已停用的专属导航条目。

## 统一装配步骤（preview → apply）

工作 1 与工作 2 的所有 `.agents/harness.json`、adapter 与快照写入均遵循同一两步门禁：

1. **预览装配并说明影响**：将 `agent`、`extensions` 与 `platforms` 写入输入，运行 `harness-install install preview --input <输入文件>`（只读，可离线运行）。审阅变更、冲突与 `projectRoot`，向用户说明项目内将写入的受管路径、目标 `agent`，以及 `apply` 可能写入目标 `agent` 全局 Skill 目录以补齐缺失的 `archify`、`smell-check`。若存在本地修改或同名冲突，先确认保留或归档策略并重新预览。
2. **应用装配**：取得确认后运行 `harness-install install apply --input <确认文件> --request-id <请求ID> --expected-revision <baseRevision>`（确认文件包含原样 `preview` 与 `confirmedBy`）。全局依赖补齐失败时，按返回的 Skill 与 agent 排查环境后重试。
