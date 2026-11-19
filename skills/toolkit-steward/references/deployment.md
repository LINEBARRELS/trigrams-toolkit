# 全局安装与恢复指引

Trigrams toolkit 的全局工具与核心 Skill 通过标准包管理器安装，不依赖源码检出目录运行：

| 组件 | 安装入口 | 说明 |
| --- | --- | --- |
| 四个公共 CLI | `uv tool install -U trigrams-toolkit` | 安装或更新 `project-state`、`plan-toolkit`、`handbook`、`harness-install`，schema、核心类型与宿主 adapter 随包交付 |
| core Skill 与核心资料 | `npx skills add LINEBARRELS/trigrams-toolkit/skills --skill '*' -g` | 将通用 Skill 及 `principles`、`workbook` 携带的核心资料全局安装至 `~/.agents/skills/`（Claude Code 如需链接至 `~/.claude/skills/`，可附加 `-a claude-code`） |
| 外部必需全局依赖 | `harness-install install apply` | 在目标项目根应用首次装配、增补或同步时，检查目标 `agent` 的全局 `archify` 与 `smell-check`，用 Vercel skills 补齐缺项 |

公共 CLI 通过 PyPI 包 `trigrams-toolkit` 分发，Skill 与扩展源维护在 `https://github.com/LINEBARRELS/trigrams-toolkit`；工具包源仓库本地开发采用 `python -m pip install -e '.[dev]'` 安装可编辑入口。`handbook` 从目标 agent 的全局 `principles`、`workbook` 读取核心资料，目标 agent 由 `--agent`、项目 `.agents/harness.json` 记录或默认值 `codex` 确定。

## 诊断与恢复

1. **CLI 命令缺失或版本异常**。确认已完成 `uv tool install`（或开发态可编辑安装）并将工具目录加入 `PATH`。可在任意目录运行 `<工具> -v` 核对四个命令的版本，或运行 `<工具> -h` 查看用法。业务命令在目标项目根执行。
2. **core Skill 缺失或不同步**：核对目标 agent 的全局 Skill 目录（Codex／Pi 为 `~/.agents/skills/`，Claude Code 为 `~/.claude/skills/` 或 `$CLAUDE_CONFIG_DIR/skills/`），使用同一 `<agent>` 重新运行 `npx skills add` 补齐或更新，消除同名异源冲突。
3. **全局依赖补齐失败**。按 `harness-install install apply` 报告的 Skill 和目标 `agent` 排查环境。确认本机 Node.js 与 `npx` 能运行当前 Vercel skills，并核对上游来源可达。修复后重试 `apply`，已装成功的 Skill 会被复用。预览及帮助可离线运行。
