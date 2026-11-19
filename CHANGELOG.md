# 更新记录

版本号以 `toolkit.json` 与 `pyproject.toml` 为准，四个公共 CLI 的 `--version` 统一来自 Python 包元数据。

## 0.1.0

- 统一发布 Python CLI 包 `trigrams-toolkit`，提供 `plan-toolkit`、`project-state`、`handbook` 与 `harness-install` 四个标准入口，并随包交付协议 schema、核心类型与宿主 adapter 模板。
- 四个 CLI 的帮助（`-h`／`--help`）与版本（`-v`／`--version`）可在任意目录查询；业务命令均在目标项目根目录执行。
- `plan-toolkit` 通过 `inspect`、`mark`、`block`、`cancel` 查询和维护计划与任务状态，Task 目录保存工作要求与交付证据。
- `project-state` 将 Module、Feature、Artifact 身份与额外关系保存在项目根的 `.project-state/state.json`，提供公共实体视图查询：`locate` 返回单实体，`related` 返回一跳 `items` 与 `relations`，`list` 返回基础视图。
- `handbook` 按正文头发现并加载全局 core、项目扩展快照与项目自建的 workbook 与 principle，支持多 ID 批量加载、`validate` 校验与 `import-principle` 原则入库。
- `harness-install` 预览并装配项目扩展快照（`.agents/extensions/<extension>/`）与宿主 adapter，保存 SHA-256 基线并在首次装配、增补或同步时补齐全局 `archify` 与 `smell-check`；提供 `archive PATH...` 归档明确的项目内相对路径。
- core Skill（`skills/`）与领域扩展（`extensions/game/`、`extensions/toolkit-maintenance/`）通过 Vercel skills 分发；`core:workbook:initialize` 随模板提供 `.gitignore`、`.ignore`、`.rgignore` 与基础项目文档结构。
- 支持 Windows 与 Linux 本机路径，并提供面向 PR 与发布候选的跨平台 CI 校验与隔离包验收流程。
