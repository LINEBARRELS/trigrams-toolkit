---
description: 在 C# 中声明类、记录、结构体、继承密封性、常量枚举或只读集合时使用。
---
# 按角色选择 C# 类型与不可变表示

声明 C# 类型、继承层次、集合属性与常量时，应按数据角色与生命周期选择恰当的语言结构：

- **类型选择：** 有身份和生命周期的概念用 `class`；按值相等的数据用 `record`；小型（通常 16 字节以内）且不可变的值用 `readonly struct` 或 `readonly record struct`。
- **继承与密封：** 多态用 `interface` 表达；需要共享实现或受保护状态时才用 `abstract class`；不打算被继承的类宜声明为 `sealed`。
- **不可变性：** 数据类型用 `init` 访问器或 `record` 位置参数；`readonly` 字段仅保证引用不变，公开集合宜以 `IReadOnlyList<T>`、`IReadOnlyDictionary<TKey, TValue>` 等只读接口暴露。
- **常量与枚举：** 编译期常量用 `const`，运行期确定或非基元类型的值用 `static readonly`；跨程序集公开的可变化值宜用 `static readonly`，避免 `const` 被内联；有限类别用 `enum`，变体携带不同数据时用 `abstract record` 加 `sealed record` 派生。
