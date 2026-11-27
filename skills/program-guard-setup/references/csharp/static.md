# C# / .NET 强可转化原则（static）

下列 principle 的核心条款可直接转化为 C# 编译器、Roslyn 分析器与架构测试的确定性检查。实际配置前，通过 `handbook load` 读取对应正文核对例外条件。

## `core:principle:programming-scale/keep-code-within-scale-limits`

- **验证工具**：Roslyn 代码度量分析器（如 .NET 内置代码度量、SonarAnalyzer 或自定义 Roslyn Analyzer）。
- **映射方向**：
  - 声明参数上限 → 方法与构造函数参数数量规则（`ref`、`out`、`in`、`params` 与扩展方法 `this` 各计 1，泛型类型参数不计）。
  - 手写源文件物理行上限与方法有效行上限 → 文件行数与方法行数度量规则（排除 `*.g.cs`、`*.Designer.cs` 等生成文件）。
  - 控制流嵌套深度上限 → 嵌套深度／认知复杂度规则。
- **档位参数**：按用户选定档位填入 `personal` / `small` / `medium`（默认）/ `large` 对应数值。

## `core:principle:programming-csharp/propagate-csharp-async-cancellation-and-dispose-resources`

- **验证工具**：.NET Code Analyzers + `Microsoft.VisualStudio.Threading.Analyzers`。
- **映射方向**：
  - 禁止同步阻塞异步链路 → 拦截 `.Result`、`.Wait()` 与 `.GetAwaiter().GetResult()` 的分析器规则。
  - 沿调用链传递取消令牌 → 强制转发 `CancellationToken` 的分析器规则。
  - 显式释放拥有资源 → 检查 `IDisposable`／`IAsyncDisposable` 未释放与 `using` 管理的分析器规则。
  - 异常重抛保留堆栈 → 拦截 `throw ex;` 破坏原始堆栈的分析器规则。
- **注意**：借用资源归属区分与长生命周期事件订阅解绑，静态分析仅能覆盖常见模式，仍应在 Review 中复核。

## `core:principle:programming-csharp/keep-csharp-method-bodies-exhaustive-and-materialized`

- **验证工具**：C# 编译器（Roslyn）+ .NET Code Analyzers。
- **映射方向**：
  - 可空引用与空值断言 → 启用可空引用上下文并将可空相关警告升错；拦截无依据的 `!` 空值宽容运算符（或要求行级豁免说明）。
  - 模式匹配与穷尽分派 → 将 `switch` 表达式非穷尽编译器警告升为错误；启用模式匹配代码样式规则（如 `IDE0019`、`IDE0020`、`IDE0078`，按项目 SDK 版本核验）替代 `as` 判空与冗余类型强转。
  - 避免 LINQ 重复枚举 → 启用检测 `IEnumerable<T>` 多次枚举的分析器规则，督促在多次遍历前物化。

## `core:principle:programming-design-module/keep-module-dependencies-acyclic`

- **验证工具**：.NET 多项目程序集引用（编译器天然禁止程序集级循环依赖）+ `NetArchTest.Rules` / `ArchUnitNET`。
- **映射方向**：
  - 多程序集拆分时，编译器直接阻断程序集间循环依赖。
  - 单程序集内跨模块命名空间，通过架构测试校验模块依赖图无环（允许单模块内部类型互引用）。

## `core:principle:programming-design-architecture/point-dependencies-inward-toward-business-decisions`

- **验证工具**：多程序集引用边界 + `NetArchTest.Rules` / `ArchUnitNET`。
- **映射方向**：
  - 识别领域决策层、编排层与外部交互层对应的程序集或命名空间。
  - 禁止领域层引用 UI、存储、网络、框架与具体第三方 SDK 命名空间，仅允许依赖基础类库与内层领域类型。

## `core:principle:programming-design-repo/name-shared-code-by-domain-knowledge`

- **验证工具**：`NetArchTest.Rules` / `ArchUnitNET` 或 `.editorconfig` 命名规则。
- **映射方向**：
  - 拦截新增的 `Utils`、`Helpers`、`Common`、`Misc` 等泛化类名或命名空间。
  - 存量项目已有历史杂物间类型时，将其加入既有豁免列表，仅阻止继续新增。
