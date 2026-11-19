# 工具包维护扩展

可选提供方 `toolkit-maintenance` 提供工具包内部的开发、维护方法与判断标准。通过 core 的 workbook 和 principles 能力按描述或稳定 ID 选择。

| workbook | 稳定 ID | 工作范围 |
| --- | --- | --- |
| [工具包扩展开发与维护](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-extension/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-extension` | 新扩展开发，以及已有扩展的修改、重构、迁移与使用方交接 |
| [知识库与 principle 审核](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-knowledge/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-knowledge` | 当前知识分类、规则归属、principle 范围与冲突 |
| [workbook 审核](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-workbook/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-workbook` | 选择描述、工作方法、配套文件、交接与验收 |
| [工具部署与调用审核](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-tooling/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-tooling` | 私有脚本、项目工具和全局 CLI 的部署及调用 |
| [Skill 审核](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-skill/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-skill` | 触发条件、主类型、职责、资料和能力调用 |

原子化判断标准位于 `skills/extension-setup-toolkit-maintenance/assets/principles/`，按六个 scope 组织：通用维护与引用（`maintenance`）、文稿防腐与契约边界（`maintenance-document`）、知识分层与原则设计（`maintenance-knowledge`）、Skill 职责与交付（`maintenance-skill`）、工具部署与调用（`maintenance-tooling`）以及 workbook 结构与交接（`maintenance-workbook`）。各 workbook 通过 `includes` 声明每次执行必读的底线原则，条件性原则通过 `handbook list --kind principle --scope <分类>` 从两字段索引按任务相关性选择并加载。

项目路径、命令、宿主和偏好作为本次输入。审核默认检查当前材料；历史读取、历史写入和 principle 生效分别遵循 core 的授权边界。新 workbook 定制仍使用 core meta workbook。

安装、升级、移除和资料查询使用 core 公共协议。本包只声明维护资源，不部署项目工具，也不接管项目自建 workbook 和知识。
