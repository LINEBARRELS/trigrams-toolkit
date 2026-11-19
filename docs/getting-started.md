# Trigrams toolkit 开发与接入

Trigrams toolkit 采用统一 Python CLI 包、Vercel skills 与项目级扩展快照分发；整体职责与分层见[架构说明](../skills/toolkit-steward/references/architecture.md)。

## 准备开发环境

需要 Python 3.11+。在仓库根安装可编辑包和开发依赖：

```sh
python -m pip install -e '.[dev]'
```

安装后提供 `project-state`、`plan-toolkit`、`handbook`、`harness-install` 四个标准入口，运行版本统一来自包元数据。当前发布版本为 `0.1.0`，数据协议版本和资料版本独立维护。CLI 运行依赖由 `pyproject.toml` 声明。

四个公共 CLI 的帮助（`-h`／`--help`）和版本（`-v`／`--version`）可在任意目录查看。其余命令须在目标项目根目录执行。

## 验证、构建与发布

仓库根目录的 [tasks.py](../tasks.py) 封装了跨平台开发、构建、验收与发布入口（零额外依赖，`python tasks.py --help` 查看全部子命令）：

```sh
python tasks.py check                  # 资源校验、协议校验与 mypy
python tasks.py check-release --tag vX.Y.Z  # 核对版本清单、CHANGELOG 与标签一致
python tasks.py test                   # 运行 tests/ 与 tests/runtime/ 全部测试
python tasks.py build                  # 清理并构建标准 sdist 与 wheel 至 dist/
python tasks.py verify-package         # 使用 uv 在仓库外隔离验收 dist/ 发行包
python tasks.py publish --test         # 可选：本地试发 TestPyPI 或应急手动上传（支持 --dry-run）
```

按改动范围也可单独运行 `tests/` 或 `tests/runtime/` 中的测试（例如 `test_project_state.py`、`test_project_paths.py`）。`build` 默认先生成 sdist 再由 sdist 构建 wheel 输出到 `dist/`，并同步在 `.tmp/direct-wheel/` 生成直接 wheel 供一致性校验；隔离验收回执保留在 `.tmp/package-check/`。命令手册与协议位于 `src/trigrams_toolkit/resources/<component>/`。

CI 在 Ubuntu 与 Windows 的 Python 3.11／3.13 上运行检查：PR 运行类型、源码校验与测试；定时任务与手动触发额外运行构建与隔离安装验收；推送 `v*` 标签由 `.github/workflows/release.yml` 完成单次构建、跨平台验收并通过 PyPI Trusted Publishing（OIDC）自动发布。具体配置见[维护说明](maintenance.md)。

## 目标安装与项目接入

分发层次与安装归属见[架构说明](../skills/toolkit-steward/references/architecture.md#5-包层次与分发边界)与[全局安装指引](../skills/toolkit-steward/references/deployment.md)：

1. **安装全局 CLI 与 core Skill**。用 `uv tool install trigrams-toolkit` 安装统一 Python 包。core Skill 用 `npx skills add LINEBARRELS/trigrams-toolkit/skills --skill '*' -g` 全局安装。Node.js 与 `npx` 遵循当前 Vercel skills 的运行要求。
2. **新项目或已有工程首次接入**。以全局 `toolkit-steward` 为入口，按[项目接入与扩展管理](../skills/toolkit-steward/references/project-integration.md)加载 `core:workbook:initialize`。在目标项目根用 `npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*'` 安装所选官方扩展 Skill（如 `game`、`toolkit-maintenance`；使用 Claude Code 时附加 `-a claude-code`），运行 `harness-install` 预览并应用装配。首次装配会检查并补齐目标 `agent` 的全局 `archify`、`smell-check`。再读取已安装的 `extension-setup-<extension>`，建立或迁移项目文档与 `AGENTS.md`。
3. **已接入项目增补扩展**。按[项目接入与扩展管理](../skills/toolkit-steward/references/project-integration.md)，在目标项目根用 `npx skills add LINEBARRELS/trigrams-toolkit/extensions/<extension>/skills --skill '*'` 安装新增扩展 Skill（Claude Code 附加 `-a claude-code`）。用完整的目标扩展集合预览并应用装配，再读取新增 setup 并合并项目约定。

工具契约与命令细节见[装配协议](../src/trigrams_toolkit/resources/installation/PROTOCOL.md)及 [Project State 协议](../src/trigrams_toolkit/resources/state/PROTOCOL.md)。
