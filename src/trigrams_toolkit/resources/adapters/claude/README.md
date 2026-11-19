# Claude Adapter

core 项目安装按所选平台将两个角色入口复制到项目 `.claude/agents/`，分别调用 `execute-task` 与 `delivery-review` Skill，无需启用领域扩展。

`src/trigrams_toolkit/resources/adapters/claude/` 是配置唯一来源，安装器按已确认预览将角色入口复制到 `.claude/agents/`。公共 CLI 与 core Skill 分别由统一 Python 包（`uv tool install`）和 Vercel skills 全局安装，项目扩展 Skill 由 Vercel skills 安装至项目（Claude Code 使用 `.claude/skills/`，兼容与 `.agents/skills/` 同树复用）；项目不预装 Plan 工具。全局安装与增补方法向 `toolkit-steward` 查询，首次接入方法通过 `handbook load core:workbook:initialize` 加载。

角色默认 `model: inherit`，权限沿用宿主。新建角色后，在新会话核对实际发现。项目 CLAUDE.md 引用已装配的 AGENTS.md，保留项目原有 Claude 规则。
