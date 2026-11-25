---
description: 创建或调整原则目录名、scope 与 description 时使用。
---
# 以具体取舍命名原则并写明触发情境

原则遵循 `principles/<scope>/<principle>/PRINCIPLE.md` 两级布局；目录名与 `description` 应直接表达核心取舍与适用时机，让调用方浏览两字段索引即可判断是否加载正文。

命名与头字段应遵循以下要求：
- `scope` 与二级目录名均应使用合法扁平 token；二级目录名采用表达具体判断或取舍的动宾或主谓短语（如 `expose-contracts-not-implementation-details`），不应使用泛化名词（如 `document-rules`、`general`）。
- YAML 头只声明 `description` 单字段，不含锚点、别名或扩展键。
- `description` 写明触发该判断的具体工作动作与情境，与同 `scope` 下其他原则形成清晰区分，不堆砌无区分度套话。
