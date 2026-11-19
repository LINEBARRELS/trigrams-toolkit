# 项目材料安装与转换

Vercel skills 将扩展 Skill 安装到项目。`harness-install` 装配项目扩展快照与平台 adapter，并在 `.agents/harness.json` 记录装配结果。全局 CLI 与 core Skill 的安装与恢复见 `toolkit-steward`。

## 材料归属与边界

| 组件 | 维护与安装方式 | 项目内位置与说明 |
| --- | --- | --- |
| 扩展 Skill | Vercel skills 按 `agent` 安装到项目 | 项目通用 skill 仓库为 `.agents/skills/`，Claude Code 位于 `.claude/skills/`（`skills-lock.json` 由 Vercel 管理） |
| 外部必需 Skill | `harness-install install apply` 调用 Vercel skills 补齐 `archify` 与 `smell-check` | 目标 `agent` 的全局 Skill 目录 |
| 扩展资源快照 | `harness-install` 从已安装的 `extension-setup-<extension>/assets/` 复制 | `.agents/extensions/<extension>/` 下的 `extension.json`、`principles/`、`workbooks/` 及配套相对文件 |
| 平台角色 adapter | `harness-install` 从统一 Python CLI 包复制 | `.codex/agents/`、`.claude/agents/` 或 `.pi/agents/`；`platforms` 支持 `codex`、`claude`、`pi-web`（与 Vercel `agent` 独立选择） |
| 声明附加材料 | `assets/extension.json` 的 `install` 字段声明 | 按声明的 `target` 与交集 `platforms` 复制并受文件基线保护 |
| 项目自有资料 | 项目自行维护 | `docs/resources.json` 不纳入 `.agents/harness.json` |

Pi Web 入口开启 `load_skills` 并继承父会话模型；使用前在宿主启用内置子代理并确认全局 core Skill 可见。上游扩展 Skill 升级后，在显式运行 `harness-install` 同步前，`handbook` 与 `project-state` 继续读取项目既有快照。

`extensions` 传入本次期望保留的**完整扩展集合**（省略时沿用已有选择，传入 `[]` 清空全部扩展）。卸载只清理受管材料，保留项目自有文稿、正式成果、Plan、项目知识与本地修改。开发调试或旧来源已缺失的迁移，可通过绝对路径 `packages` 指定来源根。

## 装配步骤

按[主 workbook](../WORKBOOK.md#必要工作流程)准备扩展并装配。调用命令时，目标平台对应两类参数：Vercel skills 的 `agent`（单选：`codex`、`claude-code`、`pi`）与宿主 adapter 的 `platforms`（多选：`codex`、`claude`、`pi-web`）。其余输入字段与参数通过 `harness-install install preview --help`、`harness-install install apply --help` 及 `--help schema` 查询。

1. **安装扩展 Skill**。若选用了扩展，运行 `npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*' -a <agent>`（官方扩展支持 `game`、`toolkit-maintenance`；第三方扩展替换为对应来源），使用与后续装配相同的 `agent`。
2. **预览装配并说明写入范围**。将 `agent`、`extensions` 与 `platforms` 写入安装输入，运行 `harness-install install preview --input <输入文件>`。预览只读，可离线生成。审阅变更、冲突及预览结果中的 `projectRoot`，并向用户说明本次装配的项目范围（项目根与将写入的受管路径）、目标 `agent`，以及 `apply` 可能写入目标 `agent` 的全局 Skill 目录（补齐缺失的 `archify`、`smell-check`）。
3. **应用装配**。如果出现本地修改或同名冲突，先与用户确认保留或归档策略并重新预览。取得确认后，运行 `harness-install install apply --input <确认文件> --request-id <请求ID> --expected-revision <baseRevision>`。确认文件包含原样的 `preview` 和 `confirmedBy`。

首次装配、增补或同步时，`install apply` 可能写入目标 `agent` 的全局 Skill 目录。它先核对预览归属、revision 与冲突，再用 Vercel skills 补齐缺失的 `archify`、`smell-check`。补齐失败时，按返回的 Skill 和 agent 检查环境并重试。项目受管文件在补齐成功后写入。

升级前完成在途装配。升级后保留符合现行格式的 `.agents/harness.json`，重新生成预览并使用新的请求 ID。

## 旧运行状态归档

若项目存在退役的 `.agents/harness.yaml`、`.agents/harness-lock.json`、不兼容的旧 `.agents/harness.json` 或待替换的旧运行状态，先停止相关写入并取得用户确认。运行 `harness-install archive PATH...`，传入互不重叠的项目内相对路径。原件移入 `.harness-archive/<批次>/` 后，重新预览并应用装配。命令细节见 `harness-install archive --help`。项目文档归档见[迁移说明](migration.md#归档与成果重建)。
