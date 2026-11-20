# C# / .NET 半可转化原则（partial）

下列 principle 仅部分条款适合静态拦截，其余条款依赖领域建模、运行时契约或人工 Review。装配配置时只落实“可静态拦截部分”，并将“留给 Review 的部分”写入交付清单。

## `core:principle:programming-csharp/choose-csharp-types-and-immutability-by-role`

- **可静态拦截**：
  - 继承密封性 → 启用“未预期继承的内部或具体类型应声明 `sealed`”分析器规则。
  - 只读集合与常量规范 → 启用集合属性避免暴露可变具体列表（如 `List<T>`）与字段优先 `readonly` 的分析器规则。
- **留给 Review**：按实体身份与值相等语义在 `class`、`record`、`struct` 间选型，以及 `readonly struct` 的复制成本与性能取舍。

## `core:principle:programming-csharp/declare-explicit-csharp-signatures-and-scale-bounds`

- **可静态拦截**：
  - 可空性契约 → 开启 `<Nullable>enable</Nullable>` 并将公开签名可空警告升错。
  - 异步签名规范 → 禁止非事件处理器使用 `async void`；要求可取消异步方法的末尾参数为 `CancellationToken`。
  - 最小可见性 → 启用可见性收窄分析器，默认使用 `private` / `internal`。
- **留给 Review**：公开入口是否完成外部输入运行时校验、可预期失败是否合理选用 `TryXxx` 或可空返回、构造函数依赖超限时是否拆分职责而非引入服务定位器。

## `core:principle:programming-design-module/expose-narrow-module-surfaces`

- **可静态拦截**：
  - 通过 `internal` 修饰配合程序集隔离，或用 `NetArchTest.Rules` / `ArchUnitNET` 限制外部模块仅依赖公开入口命名空间。
- **留给 Review**：接口是否按调用方拆分、公开返回值是否泄漏内部数据结构。

## `core:principle:programming-design-abstraction/push-side-effects-to-orchestration-edges`

- **可静态拦截**：
  - 在已拆分的纯业务程序集或命名空间中，通过架构测试禁止引用 `System.IO`、`System.Net.Http`、数据库客户端及系统静态时钟等副作用入口。
- **留给 Review**：未按命名空间隔离的类型内部，纯规则计算与状态修改是否混杂在同一方法中。

## `core:principle:programming-design-abstraction/assign-a-single-owner-to-mutable-state`

- **可静态拦截**：
  - 启用 Roslyn 分析器拦截可写的 `public static` 字段与未加 `readonly` 的共享静态成员。
- **留给 Review**：跨对象可变引用写归属、资源释放所有权以及多线程同步策略选择。

## `core:principle:programming-design-abstraction/wrap-third-party-apis-at-project-boundaries`

- **可静态拦截**：
  - 通过 `NetArchTest.Rules` / `ArchUnitNET` 限制指定第三方 NuGet 命名空间仅允许在适配器程序集或指定包装命名空间内引用。
- **留给 Review**：包装接口是否使用项目领域类型、是否将第三方异常转换为项目失败语义。

## `core:principle:programming-pragmatic/enforce-strict-boundaries-with-lightweight-internals`

- **可静态拦截**：
  - 对 `public` 入口方法启用参数空值校验分析器，配合严格可空编译守住边界契约。
- **留给 Review**：信任边界校验是否覆盖全部外部输入，以及内部实现是否避免冗余校验与过度包装。

## 显式禁区（不转化为静态规则）

下列高频语义原则在 C# 工具链中缺乏可靠静态判据，不应强行编写启发式分析器规则：

- `core:principle:programming-design-abstraction/extract-shared-knowledge-not-coincidental-shape`：禁止用代码查重工具强制合并形似但变化轴不同的代码。
- `core:principle:programming-review/eliminate-surplus-indirection`：静态分析无法可靠区分“冗余转发包装”与“为依赖倒置设立的合法边界接口”。
- `core:principle:programming-review/expose-hidden-change-coupling`：跨模块隐式同步约定与双真相源无法由编译器发现，应留给设计审查与状态不变量测试。
