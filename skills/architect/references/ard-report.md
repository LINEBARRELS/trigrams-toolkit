# ARD 单页报告

阅读维护后的 ARD 与项目 DEVTECH，沿用项目约定的文档路径。使用 `archify` skill 的 `explainer` 模式，将 `tree` 与 `architecture` 两张图整合为单页报告。页首概括架构设计结论，修订时说明本次变化。

## 架构树

生成 `tree` 图，以项目为根，按 `Architecture Layer → Module → Feature` 展开。沿用 ARD 中的名称与归属，节点简述职责；已有 Module、Feature ID 放入说明。高亮本次新增、修改或迁移的项。

## 依赖与边界

生成 `architecture` 图，以 ARD 的架构层级与 Module 职责为骨架，结合 DEVTECH 中的宏观职责、依赖方向、所有权与跨层入口，展示系统协作关系。以 Module 为主体，按文档展开参与跨模块协作的 Feature 与外部依赖，标明职责边界、关系方向和调用、依赖、读写等关系含义。

必要关系与影响行为的条件保留在节点或连线上，补充解释收入卡片。高亮本次变更涉及的边界与关系。

## 单页组织

通过 `explainer` 整合图表，文字补充设计依据与变更影响。
