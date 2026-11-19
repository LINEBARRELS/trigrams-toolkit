---
name: 工具部署与调用审核
description: 追踪 Skill 私有脚本、项目工具和全局 CLI 从维护源到实际调用的路径，核对材料、协议、依赖及恢复证据。用于部署改动、定位失败或独立运行验收前审核。
resourceId: toolkit-maintenance:workbook:maintenance-tooling
includes:
- toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence
- toolkit-maintenance:principle:maintenance-tooling/separate-public-cli-from-private-scripts
---

# 工具部署与调用审核

## 适用与输入

取得目标工具、调用方、宿主、安装方式（如 `uv tool install`、可编辑开发安装、Vercel skills 或项目快照）和已知来源。提供工具手册、命令契约、安装记录及运行证据，明确本次授权范围。默认以只读方式追踪调用链。

## 必要工作流程

1. 从调用方追踪工具入口、执行代码、schema、配置与证据，依据必读原则 `separate-public-cli-from-private-scripts` 定位每项材料的责任归属、安装来源与 `assets/extension.json`／`docs/resources.json`（`resourceRoots`、`install`）或 Python 包声明一致性。
2. 在目标项目根运行 `handbook list --kind principle --scope maintenance-tooling --scope maintenance --scope maintenance-document`，按本次核查重点选择并 `handbook load` 条件原则：
   - 审核 Skill、workbook 或说明文稿中的 CLI 调用写法时，加载 `maintenance-tooling/specify-cli-action-context-not-flag-manuals` 与 `maintenance-document/expose-contracts-not-implementation-details`。
   - 审核或实测 CLI 的 `-h`/`--help` 行为、安装部署状态保护与中断恢复时，加载 `maintenance-tooling/keep-cli-help-and-state-writes-safe`。
   - 核查跨组件引用可达性或契约单点维护时，从 `maintenance` 加载 `keep-reference-chains-reachable-and-complete` 或 `keep-one-authoritative-source-per-rule`。
3. 从项目外目录执行受影响的公共 CLI 的 `-h`／`--help` 和 `-v`／`--version`。比对帮助信息与参数、输入和返回值。
4. 按变更风险设计隔离试验。在隔离项目根验证 CLI、资源同步、基线保护与依赖失败后的重试。涉及 `harness-install install apply` 时隔离目标 `agent` 的全局 Skill 目录，并核对受管文件的写入顺序。

## Task 切分与交接

审核由 general Task 交付。需要整改时，通过 `dependsOn` 衔接审核、整改与复验。整改消费审核问题与证据，整改后从真实部署入口复验，确保部署环境行为一致。

## 产出与验收

交付调用路径、材料归属、依赖拓扑、差异说明、实际运行日志与未验证项。各项结论均能定位到实际入口与调用证据，明确复制独立性与中断恢复结果。
