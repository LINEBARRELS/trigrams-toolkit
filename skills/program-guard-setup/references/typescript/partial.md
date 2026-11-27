# TypeScript / JavaScript 半可转化原则（partial）

下列 principle 仅部分条款适合静态拦截，其余条款依赖领域建模、运行时契约或人工 Review。装配配置时只落实“可静态拦截部分”，并将“留给 Review 的部分”写入交付清单。

## `core:principle:programming-typescript-javascript/declare-explicit-ts-module-boundaries-and-results`

- **可静态拦截**：
  - 禁止外部代码深层导入模块内部文件 → `package.json` 的 `exports` 字段、`dependency-cruiser` 或 `eslint-plugin-boundaries` 限制仅从模块公开入口导入。
  - 模块公开导出清晰 → `no-restricted-syntax` 或导出规范限制通配 `export *`（按项目约定选用），配合 `explicit-module-boundary-types` 约束公开函数签名。
- **留给 Review**：外部未验证数据是否都在入口完成运行时校验（如 Zod / Valibot）、可预期失败是否合理选用 `undefined` 或结果联合类型、对象参数是否沦为无关字段的 `options` 大包。

## `core:principle:programming-typescript-javascript/model-ts-states-with-discriminated-unions-and-brands`

- **可静态拦截**：
  - 数据字段与数组不可变 → `typescript-eslint` 的 `prefer-readonly` 及只读数组／参数约定；若项目约定禁用 `enum`，可用 `no-restricted-syntax` 拦截 `TSEnumDeclaration`。
- **留给 Review**：互斥状态是否用可辨识联合替代多布尔组合、静态配置表与策略路由映射是否使用 `satisfies` 保留字面量推导并替代单对象字符串分支、哪些原始类型 ID 应声明 Brand 类型、以及多态场景下 `interface` 与 `class` 的取舍。

## `core:principle:programming-typescript-javascript/control-js-promise-concurrency-and-avoid-aliasing-traps`

- **可静态拦截**：
  - 禁止浮动 Promise → `typescript-eslint` 的 `no-floating-promises`。
  - 禁止 `forEach(async ...)` 等异步回调误用 → `no-misused-promises`。
  - 避免 `||` 误吞 `0`、`""`、`false` → `prefer-nullish-coalescing`。
- **留给 Review**：批量并发是否按外部容量限流、闭包变量捕获以及 `{ ...obj }` 浅拷贝引发的共享状态别名修改。

## `core:principle:programming-design-module/expose-narrow-module-surfaces`

- **可静态拦截**：
  - 仅允许从模块入口文件导出公开 API，阻止调用方绕过入口直接引用内部实现文件（`dependency-cruiser`、`eslint-plugin-boundaries` 或 `no-restricted-imports`）。
- **留给 Review**：接口是否按调用方职责拆分、公开返回值是否泄漏内部数据结构或诱导链式穿透访问。

## `core:principle:programming-design-abstraction/push-side-effects-to-orchestration-edges`

- **可静态拦截**：
  - 在已拆分的纯业务决策目录下，通过 ESLint `no-restricted-imports` 与 `no-restricted-globals` 禁用 `node:fs`、`node:http`、`fetch`、`process.env`、`Date.now`、`Math.random` 等 I/O 与非确定性副作用。
- **留给 Review**：未按目录隔离的模块内部，纯计算逻辑与状态修改是否混杂在同一函数中。

## `core:principle:programming-design-abstraction/assign-a-single-owner-to-mutable-state`

- **可静态拦截**：
  - 禁用 `var`（`no-var`）、优先 `const`（`prefer-const`）、禁止导出可变绑定（`import/no-mutable-exports`）以抑制模块级隐式共享可变状态。
- **留给 Review**：跨对象传递的可变引用归属、资源释放与事件订阅解绑生命周期、异步并发写入同步策略。

## `core:principle:programming-design-abstraction/wrap-third-party-apis-at-project-boundaries`

- **可静态拦截**：
  - 在业务代码目录通过 `no-restricted-imports` 或 `dependency-cruiser` 禁止直接导入指定第三方 SDK（如数据库驱动、支付或第三方 HTTP 客户端），只放行约定的 `adapters/` 或包装模块目录。
- **留给 Review**：包装层接口是否使用项目领域类型、是否将第三方异常翻译为项目失败语义。

## `core:principle:programming-pragmatic/enforce-strict-boundaries-with-lightweight-internals`

- **可静态拦截**：
  - 在边界入口文件禁止 `any` 与不安全断言，配合 `tsconfig` 严格模式迫使外部输入以 `unknown` 进入。
- **留给 Review**：信任边界的校验是否覆盖全部外部输入，以及内部实现是否避免冗余防御与过度包装。

## 显式禁区（不转化为静态规则）

下列高频语义原则在 TypeScript 工具链中缺乏可靠静态判据，不应强行编写启发式 Lint 规则：

- `core:principle:programming-design-abstraction/extract-shared-knowledge-not-coincidental-shape`：禁止用代码查重工具（如 AST 重复检测）强制合并形似但变化轴不同的代码。
- `core:principle:programming-review/eliminate-surplus-indirection`：静态工具无法可靠区分“冗余转发包装”与“为依赖倒置设立的合法边界接口”。
- `core:principle:programming-review/expose-hidden-change-coupling`：跨模块隐式同步约定与双真相源无法由类型系统或语法检查发现，应留给设计审查与状态不变量测试。
- `core:principle:programming-review/reject-test-fitted-domain-models`：类型系统与 ESLint 无法识别将通用状态机退化为单次探针特例或硬编码测试夹具常量的建模缺陷，应留给架构与代码审查。
