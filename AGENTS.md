# 八卦 Trigrams toolkit

本仓库维护跨领域的 Agent 工具包，采用 Vercel skills 分发、统一 Python CLI 包与项目级扩展装配。

自有 Skill 位于 `skills/`，扩展资源位于各 setup 的 `assets/`；四个公共 CLI（`project-state`、`plan-toolkit`、`handbook`、`harness-install`）统一维护在 `src/trigrams_toolkit/`，契约、核心类型与平台 adapter 随包内 `resources/` 交付。

## 常用入口

- [开发与接入](docs/getting-started.md)：开发环境准备、源码校验与三段安装接入流程。
- [维护与发布](docs/maintenance.md)：唯一维护源、定向验证与打包发布入口。
- [架构说明](skills/toolkit-steward/references/architecture.md)：体系职责、知识分层与分发边界。
- [项目决策索引](docs/knowledge/decisions/index.md)：已确立的核心架构与工具契约取舍。

## 工作约定

- 代码开发时，从[现有原则目录](skills/principles/principles)按任务和语言查找相关 `PRINCIPLE.md`，直接读取并用于设计、实现与审查。
- 四个公共 CLI 的帮助（`-h`／`--help`）和版本（`-v`／`--version`）可在任意目录查看。其余命令须在目标项目根目录执行。
- 临时文件、过程日志和调试输出放在项目根 `.tmp/`。
- 历史 Plan、Task、交付证据和审核记录保留原样。
- 修改维护源后，运行 `python tasks.py check` 及对应测试；打包、验收与发布统一使用根目录 [tasks.py](tasks.py)。
