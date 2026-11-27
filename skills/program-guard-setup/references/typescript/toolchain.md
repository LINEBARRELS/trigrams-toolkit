# TypeScript / JavaScript 验证工具链

本文件提供 TypeScript / JavaScript 项目主流验证工具的分工与官方文档入口。项目既有工具栈的识别、配置格式、规则名称与校验命令，均以目标项目实际安装版本及对应官方文档为准。

## 主流验证工具分工与官方文档

已有对应类别的工具时优先复用，不无故更换现有生态。

| 验证层次 | 推荐工具 | 负责范围 | 官方文档 |
| --- | --- | --- | --- |
| 类型与控制流收窄 | TypeScript (`tsc`) | 严格可空性、索引安全、`satisfies` 契约校验、类型谓词收窄、`never` 穷尽检查 | [TSConfig Reference](https://www.typescriptlang.org/tsconfig/) |
| 语法与类型感知 Lint | ESLint + `typescript-eslint` | 禁 `any`／非空断言、浮动 Promise、穷尽 `switch`、代码规模指标、受限导入 | [ESLint Rules](https://eslint.org/docs/latest/rules/) · [typescript-eslint Rules](https://typescript-eslint.io/rules/) |
| 高速基础 Lint（既有选用时） | Biome | 格式化与高频基础 Lint；跨文件类型流分析仍由 `tsc` 或 `typescript-eslint` 补足 | [Biome Linter Rules](https://biomejs.dev/linter/rules/) |
| 模块依赖图与分层边界 | `dependency-cruiser` | 无环依赖、跨层单向依赖、禁止深层导入内部文件、目录命名约束 | [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) |
| ESLint 内联分层约束（轻量替代） | `eslint-plugin-boundaries` | 按目录元素类型限制跨层与跨模块 `import` | [eslint-plugin-boundaries](https://github.com/javierbrea/eslint-plugin-boundaries) |
