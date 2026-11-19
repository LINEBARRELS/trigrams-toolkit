---
name: 工具包扩展开发与维护
description: 开发新扩展，或修改、重构和迁移已有扩展，维护职责、资源组织、安装关系与使用方交接。用于扩展整体交付；单类材料审核采用对应审核 workbook。
resourceId: toolkit-maintenance:workbook:maintenance-extension
includes:
- toolkit-maintenance:principle:maintenance/keep-one-authoritative-source-per-rule
- toolkit-maintenance:principle:maintenance/keep-reference-chains-reachable-and-complete
---

# 工具包扩展开发与维护

## 适用与输入

取得工作目标、扩展维护源、代表性使用场景和目标环境。维护已有扩展时，补充当前包声明、材料、安装来源、实际使用方和相关 Plan。缺项只限制依赖该输入的工作；假设场景标明待核实条件。

## 必要工作流程

扩展承载领域能力，沿用 core 的 Plan、资料发现和安装协议。新扩展先明确领域职责、预期成果与 core 的边界。按代表性工作选择所需材料：

| 结构 | 职责与维护要求 |
| --- | --- |
| `assets/extension.json` | 在 `extension-setup-<extension>` 内声明扩展名、版本、资源根、附加 `install` 材料与可选领域类型／关系。新扩展接入仓库 `toolkit.json` 与 Skill 发现入口 |
| `extension-setup-<extension>` | 设置 `disable-model-invocation: true`（避免常驻日常上下文），由 `core:workbook:project-setup` 按项目 Skill 路径直接读取；正文按四段正交结构维护：1. 资源结构与依赖检查、2. 特定目录路径、3. 项目级文档补充与新增（含移除清理项）、4. 存量迁移与归档建议（按需） |
| `workbooks/`、`principles/`、领域 Skill | 分别保存工作方法、判断标准和行为入口；按代表目标选择材料，维护可发现的身份与读取关系 |
| 附加材料、公共工具与 adapter | 确需装配到项目的材料在 `extension.json` 的 `install` 中声明；公共 CLI 与宿主 adapter 由统一工具包维护，安装与装配方式向 `toolkit-steward` 查询 |

1. 沿代表性工作核对职责与材料分工。复用 core 和已有扩展能力，确定本次新增、修改或退役的内容。
2. 从改动点追踪引用、调用和安装关系。核对使用方与未完成 Task；资源身份或工作依据变化影响在途工作时，调用 `effect` 取得承接范围。
3. 按本次涉及的材料类型，运行 `handbook list --kind principle --scope <对应scope>` 查看可用原则，按 `description` 选择并 `handbook load` 所需判断（如调整资源身份时加载 `maintenance-knowledge/sync-active-references-on-identity-change`，编写或精简文稿时从 `maintenance-document` 选择对应防腐原则）。修改唯一维护源，同步受影响的包声明、入口、引用、契约与说明。
4. 按材料选择本扩展对应的 Skill、workbook、知识或工具审核 workbook 完成核查。
5. 按改动范围验证。资源变化检查发现与加载，方法变化演练代表性任务。扩展 Skill、声明或材料变化后，通过 Vercel skills 更新。在项目根用 `harness-install` 预览并应用装配，刷新项目快照。公共工具或包内 adapter 变化时更新安装包并验证调用。工具包源仓库的静态校验与打包验证按仓库维护文档执行。

## Task 切分与交接

按独立交付结果切分 Task。职责或公共契约待确定时，先交付设计依据，后续实现通过 `dependsOn` 等待完整成果。围绕扩展的核心成果，结合工作目标、成果结构和现状划定 Stub。

涉及使用方迁移时，交接新旧资源身份、安装选择、目标环境及待修订工作。项目快照与平台 adapter 由 `harness-install` 维护安装记录（`.agents/harness.json`），Skill 目录由 Vercel skills 管理。

## 产出与验收

交付扩展源包、受影响使用方的承接结果与验证证据。在项目根运行 `handbook validate` 校验涉及的资源来源，并按改动范围完成源包与契约检查。

确认资源可发现、引用可解析，代表性工作可完成。涉及安装时，核对实际材料与声明一致，移除只清理受管材料并保留项目成果、Plan 和知识。分别记录通过、失败、未运行及补验条件。
