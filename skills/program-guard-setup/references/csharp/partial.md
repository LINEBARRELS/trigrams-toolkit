# C# / .NET 半可转化原则（partial）

下列 principle 仅部分条款适合静态拦截，其余条款依赖领域建模、运行时契约或人工 Review。装配配置时只落实“可静态拦截部分”，并将“留给 Review 的部分”写入交付清单。

## `core:principle:programming-csharp/choose-csharp-types-and-immutability-by-role`

- **可静态拦截**：
  - 必传初始化与可空闭合 → 开启可空引用检查并将未初始化非空属性警告（`CS8618`）升错，迫使对象初始化器必传成员显式声明 `required` 或通过构造函数赋值。
  - 继承密封性 → 启用“未预期继承的内部或具体类型应声明 `sealed`”分析器规则。
  - 只读集合与常量规范 → 启用集合属性避免暴露可变具体列表（如 `List<T>`）与字段优先 `readonly` 的分析器规则。
- **留给 Review**：按身份与值相等语义在 `class`、`record`、`struct` 间选型、闭合变体（`abstract/sealed record`）与开放接口多态取舍、以及是否用无业务含义的空字符串默认值掩盖必传状态。

## `core:principle:programming-csharp/declare-explicit-csharp-signatures-and-scale-bounds`

- **可静态拦截**：
  - 可空性契约 → 开启 `<Nullable>enable</Nullable>` 并将公开签名可空警告升错。
  - 异步与流式签名规范 → 禁止非事件处理器使用 `async void`；要求可取消异步方法的末尾参数为 `CancellationToken`，并将 `IAsyncEnumerable<T>` 缺失 `[EnumeratorCancellation]` 的警告（`CS8425`）升错。
  - 最小可见性 → 启用可见性收窄分析器，默认使用 `private` / `internal`。
- **留给 Review**：公开入口是否完成外部输入运行时校验、异步流式产出是否合理选用 `IAsyncEnumerable<T>` 替代全量缓冲、构造函数依赖超限时是否拆分职责而非引入服务定位器。

## `core:principle:programming-csharp/prefer-csharp-compile-time-dispatch-and-spans`

- **可静态拦截**：
  - 限域禁用反射与引导源生成 → 通过 `Microsoft.CodeAnalysis.BannedApiAnalyzers` 或 `NetArchTest.Rules` / `ArchUnitNET` 在业务程序集中限制直接调用 `System.Reflection`；启用内置源生成提示规则（如引导使用 `[GeneratedRegex]` 与序列化源生成告警）。
- **留给 Review**：泛型内是否以 `static abstract` 接口约束替代 `typeof(T)` 分支、外部配置标识是否在组合根经 `FrozenDictionary` 单次查表转为接口多态、常规逻辑是否滥用 `dynamic`、以及高频解析路径是否采用 `ReadOnlySpan<T>`。

## `core:principle:programming-design-module/expose-narrow-module-surfaces`

- **可静态拦截**：
  - 通过 `internal` 修饰配合程序集隔离，或用 `NetArchTest.Rules` / `ArchUnitNET` 限制外部模块仅依赖公开入口命名空间。
- **留给 Review**：接口是否按调用方拆分、公开返回值是否泄漏内部数据结构。

## `core:principle:programming-design-abstraction/push-side-effects-to-orchestration-edges`

- **可静态拦截**：
  - 在已拆分的纯业务程序集或命名空间中，通过架构测试禁止引用 `System.IO`、`System.Net.Http`、数据库客户端及系统静态时钟等副作用入口。
- **留给 Review**：未按命名空间隔离的类型内部，纯规则计算与状态修改是否混杂在同一方法中。

## `core:principle:programming-design-state/assign-a-single-owner-to-mutable-state`

- **可静态拦截**：
  - 启用 Roslyn 分析器拦截可写的 `public static` 字段与未加 `readonly` 的共享静态成员。
- **留给 Review**：跨对象可变引用写归属、资源释放所有权以及多线程同步策略选择。

## `core:principle:programming-design-abstraction/wrap-third-party-apis-at-project-boundaries`

- **可静态拦截**：
  - 通过 `NetArchTest.Rules` / `ArchUnitNET` 限制指定第三方 NuGet 命名空间仅允许在适配器程序集或指定包装命名空间内引用。
- **留给 Review**：包装接口是否使用项目领域类型、是否将第三方异常转换为项目失败语义。

## `core:principle:programming-design-architecture/validate-external-input-at-trust-boundaries`

- **可静态拦截**：
  - 对 `public` 入口方法启用参数空值校验分析器，配合严格可空编译守住边界契约。
- **留给 Review**：外部输入是否在进入内部代码前完成运行时校验，内部调用是否能依赖已建立的约束。

## 显式禁区（不转化为静态规则）

下列高频语义原则在 C# 工具链中缺乏可靠静态判据，不应强行编写启发式分析器规则：

- `core:principle:programming-design-abstraction/extract-shared-knowledge-not-coincidental-shape`：禁止用代码查重工具强制合并形似但变化轴不同的代码。
- `core:principle:programming-review/eliminate-surplus-indirection`：静态分析无法可靠区分“冗余转发包装”与“为依赖倒置设立的合法边界接口”。
- `core:principle:programming-review/find-hidden-dependencies-in-rules-state-and-call-order`：跨模块隐式同步约定与双真相源无法由编译器发现，应留给设计审查与状态不变量测试。
- `core:principle:programming-review/reject-test-fitted-domain-models`：编译器与分析器仅校验类型自洽，无法识别将通用多步业务焊死为固定字段或硬编码测试探针常量的退化建模，应留给架构与代码审查。
