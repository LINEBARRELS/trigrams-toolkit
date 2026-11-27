---
description: 在 C# 中声明公开方法签名、可空性、失败语义、异步与流式取消契约或核对声明规模时使用。
---
# 显式声明 C# 签名契约与规模口径

编写 C# 公开签名、属性与类型结构时，应明确表达可空性、失败与异步契约，并遵守声明期规模口径：

- **可空性：** 签名中的 `?` 只标在确实可能为空的参数和返回值上；可空标注不提供运行时检查，公开入口仍应校验外部输入。
- **失败语义：** 可预期的失败用 `bool TryXxx(..., out T result)` 或可空返回值表达；违反调用前提时抛出 `ArgumentException` 系列异常。
- **异步与流式签名：** 异步操作返回 `Task`／`Task<T>`，高频且常同步完成的路径可返回 `ValueTask`；异步流式产出序列宜返回 `IAsyncEnumerable<T>`（配合 `[EnumeratorCancellation] CancellationToken`）替代全量缓冲 `Task<List<T>>`；可取消操作的末尾参数为 `CancellationToken`，`async void` 仅用于要求 `void` 的事件处理器。
- **可见性：** 默认使用最小可见性（`private` → `internal` → `public`），程序集内部共享类型用 `internal`。
- **声明规模口径：** `ref`、`out`、`in`、`params` 及扩展方法 `this` 参数各计 1，泛型类型参数不计；构造函数依赖超限时检查类型职责，不用服务定位器或通用上下文对象隐藏依赖；文件行数超限时检查是否定义了多个主要类型。
