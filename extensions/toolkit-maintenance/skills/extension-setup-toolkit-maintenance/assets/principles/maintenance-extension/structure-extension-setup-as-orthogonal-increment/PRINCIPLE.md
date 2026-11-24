---
description: 创建、修改或审核 extension-setup-<name>/SKILL.md 及同目录 agents/openai.yaml 时使用。
---
# 按四段正交增量构建扩展 Setup Skill

扩展接入入口 `extension-setup-<name>/SKILL.md` 应作为按需读取的增量说明，而非默认常驻上下文的日常工作流，与 `core:workbook:project-setup` 保持正交分工。

维护 Setup 入口时应满足以下契约：
- YAML 头应声明 `name: extension-setup-<name>`、非空 `description`、`disable-model-invocation: true` 及 `metadata.harness-toolkit-type: workflow`；同目录 `agents/openai.yaml` 应配置 `policy.allow_implicit_invocation: false`。
- 正文应固定包含四段正交增量章节：1. 资源结构与依赖检查；2. 特定目录路径；3. 项目级文档补充与新增（须含移除扩展时的清理项）；4. 存量迁移与归档建议（按需）。
- Setup 入口只补充该扩展的增量约定，不接管 core `docs/` 骨架、不强装项目工具，也不创建无用途的空占位目录。
