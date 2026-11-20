# C# / .NET 验证工具链

本文件提供 C# / .NET 项目主流验证工具的分工与官方文档入口。项目既有工具栈的识别、配置格式、规则名称与校验命令，均以目标项目实际安装版本及对应官方文档为准。

## 主流验证工具分工与官方文档

已有对应类别的工具时优先复用，不无故更换现有生态。

| 验证层次 | 推荐工具 | 负责范围 | 官方文档 |
| --- | --- | --- | --- |
| 编译期类型与空值检查 | C# 编译器（Roslyn） | 可空引用类型、`switch` 表达式穷尽性、指定警告升错 | [C# Compiler Options](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/) |
| 内置代码质量与风格分析 | .NET Code Analyzers + `.editorconfig` | 资源释放、`CancellationToken` 传递、异常堆栈保留、集合枚举与代码风格 | [.NET Code Analysis](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview) |
| 异步与并发陷阱分析 | `Microsoft.VisualStudio.Threading.Analyzers` | 拦截 `.Result`／`.Wait()` 同步阻塞、`async void` 与异步链路误用 | [VisualStudio.Threading Analyzers](https://github.com/microsoft/vs-threading/blob/main/doc/analyzers/index.md) |
| 架构与依赖边界测试 | `NetArchTest.Rules` / `ArchUnitNET` | 跨命名空间无环依赖、分层单向依赖、可见性与命名规范检查 | [NetArchTest](https://github.com/BenMorris/NetArchTest) · [ArchUnitNET](https://github.com/TNG/ArchUnitNET) |
