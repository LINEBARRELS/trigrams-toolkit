# Python 半可转化原则（partial）

下列 principle 仅部分条款适合静态拦截，其余条款依赖领域建模、运行时契约或人工 Review。装配配置时只落实“可静态拦截部分”，并将“留给 Review 的部分”写入交付清单。

## `core:principle:programming-python/model-python-data-and-protocols-with-explicit-types`

- **可静态拦截**：
  - 公开函数与入口完整类型注解 → Pyright / mypy 严格模式强制参数与返回值注解，校验 `Final` 常量不可重赋值、`NewType` 区分、`TypeIs`／`TypeGuard` 收窄以及 `Protocol` 结构化匹配。
  - 枚举与联合变体穷尽分派 → 启用 Pyright 严格穷尽检查或 mypy `exhaustive-match` 错误码，配合 `match/case` 与 `typing.assert_never` 拦截遗漏分支。
- **留给 Review**：外部字典输入是否在入口完成运行时校验（注解、`TypedDict` 与 `NewType` 无运行时检查）、`@dataclass(frozen=True)`／`NamedTuple`／`TypedDict` 选型、以及开放变体是否通过 `Protocol`／`ABC` 与边界字典查表替代单类字符串 `if-elif` 分支。

## `core:principle:programming-python/manage-python-coroutines-and-keep-iterators-flat`

- **可静态拦截**：
  - 协程遗漏等待与异步阻塞 → Pyright 未等待协程告警 + Ruff 异步规则族（拦截常见异步函数内同步阻塞 I/O 与睡眠调用）。
  - 推导式过载 → 限制过深嵌套推导式与高复杂度单行表达式。
- **留给 Review**：并发任务是否交由 `TaskGroup` 或明确管理者托管、取消后的清理与 `CancelledError` 传播、以及生成器一次性遍历陷阱。

## `core:principle:programming-design-module/expose-narrow-module-surfaces`

- **可静态拦截**：
  - 通过 `import-linter`、`tach` 或 Ruff 私有导入规则，禁止外部代码绕过包 `__init__.py` 公开入口直接深层导入内部实现模块。
- **留给 Review**：接口是否按调用方拆分、公开返回值是否暴露内部数据结构。

## `core:principle:programming-design-abstraction/push-side-effects-to-orchestration-edges`

- **可静态拦截**：
  - 在已拆分的纯业务决策包下，通过 `import-linter`、`tach` 或 Ruff 禁用 API 规则，禁止导入 `os`、`pathlib`、`subprocess`、网络客户端与全局系统时钟等副作用模块。
- **留给 Review**：未按包隔离的模块内部，纯规则计算与状态修改是否混杂在同一函数中。

## `core:principle:programming-design-state/assign-a-single-owner-to-mutable-state`

- **可静态拦截**：
  - 通过 Ruff 拦截 `global` 语句与可变默认参数，抑制隐式共享可变状态。
- **留给 Review**：模块级可变容器、跨对象共享可变列表／字典的写归属，以及线程／协程并发同步策略。

## `core:principle:programming-design-abstraction/wrap-third-party-apis-at-project-boundaries`

- **可静态拦截**：
  - 通过 `import-linter`、`tach` 或 Ruff 禁用导入规则，限制指定第三方库仅允许在适配层或指定包装模块导入。
- **留给 Review**：包装接口是否使用项目领域类型、是否将第三方异常翻译为项目基异常语义。

## `core:principle:programming-design-architecture/validate-external-input-at-trust-boundaries`

- **可静态拦截**：
  - 在边界入口模块启用 Pyright / mypy 严格模式，禁止公开签名退化为裸 `Any` 与隐式未知类型。
- **留给 Review**：外部输入是否在进入内部代码前完成运行时校验，内部调用是否能依赖已建立的约束。

## 显式禁区（不转化为静态规则）

下列高频语义原则在 Python 工具链中缺乏可靠静态判据，不应强行编写启发式 Lint 规则：

- `core:principle:programming-design-abstraction/extract-shared-knowledge-not-coincidental-shape`：禁止用代码查重工具强制合并形似但变化轴不同的代码。
- `core:principle:programming-review/eliminate-surplus-indirection`：静态分析无法可靠区分“冗余转发包装”与“为依赖倒置设立的合法边界接口”。
- `core:principle:programming-review/find-hidden-dependencies-in-rules-state-and-call-order`：跨模块隐式同步约定与双真相源无法由类型检查或 Linter 发现，应留给设计审查与状态不变量测试。
- `core:principle:programming-review/reject-test-fitted-domain-models`：类型检查与 Linter 无法判断数据模型或状态分支是否面向单次验收样例退化硬编码，应留给架构与代码审查。
