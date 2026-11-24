# 工具包维护扩展

可选拓展 `toolkit-maintenance` 提供工具包内部的扩展开发与结构合规工作方法，以及面向工具包日常维护的原子化判断标准。通过 core 的 workbook 和 principles 能力按描述或稳定 ID 选择。

| workbook | 稳定 ID | 工作范围 |
| --- | --- | --- |
| [工具包扩展开发与维护](skills/extension-setup-toolkit-maintenance/assets/workbooks/maintenance-extension/WORKBOOK.md) | `toolkit-maintenance:workbook:maintenance-extension` | 新扩展开发，以及已有扩展的重构、迁移与结构合规核验 |

原子化判断标准位于 `skills/extension-setup-toolkit-maintenance/assets/principles/`，按六个 scope 组织：通用维护与文稿契约（`maintenance`）、扩展架构与包边界（`maintenance-extension`）、知识分层与原则设计（`maintenance-knowledge`）、workbook 范式与规则槽位（`maintenance-workbook`）、Skill 职责与交付（`maintenance-skill`）以及工具部署与契约闭环（`maintenance-tooling`）。`maintenance-extension` 通过 `includes` 声明每次执行必读的底线原则，并在规则槽位中按材料类型指引通过 `handbook list --kind principle --scope <分类>` 按需加载其余原则。

项目路径、命令、宿主和偏好作为本次输入。审核默认检查当前材料；历史读取、历史写入和 principle 生效分别遵循 core 的授权边界。通用定制 workbook 仍使用 core meta workbook，源码改动衔接 core `programming-development`。

安装、升级、移除和资料查询使用 core 公共协议。本包只声明维护资源，不部署项目工具，也不接管项目自建 workbook 和知识。
