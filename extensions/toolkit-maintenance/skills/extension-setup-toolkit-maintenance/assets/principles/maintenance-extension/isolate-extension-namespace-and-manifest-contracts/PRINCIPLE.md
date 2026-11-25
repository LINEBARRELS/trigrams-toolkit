---
description: 编写或审核 assets/extension.json 的标识、类型、关系与 install 映射时使用。
---
# 隔离扩展命名空间与清单安装边界

扩展清单 `assets/extension.json` 应以自身扩展名为命名空间边界，严格隔离领域类型声明与文件装配权限，不越界污染 core 或目标项目受管路径。

编写与审核 `extension.json` 时应遵守以下规则：
- `schemaVersion` 固定为 `1`；`extension` 应为合法扁平 token，且不应占用 `core` 或 `project` 保留标识；`version` 符合版本规范并与发布配置对齐。
- 声明的 `artifactTypes` 与 `relationTypes[*].kind` 均应带 `<extension>:` 前缀，不允许覆盖或重定义 core 及其他扩展的类型。
- `install` 条目只装配项目确需的模板或扩展材料，不应复制 `SKILL.md` 或 `tools/`，不应写入受保护的核心路径或宿主配置目录，也不应覆盖 `.agents/extensions/<name>/` 受管快照目录。
