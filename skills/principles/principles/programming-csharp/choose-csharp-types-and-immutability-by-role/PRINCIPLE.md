---
description: 在 C# 中声明类、记录、结构体、必传初始化属性、继承密封性、常量枚举或只读集合时使用。
---
# 按角色选择 C# 类型与不可变表示

声明 C# 类型、初始化契约、继承层次、集合属性与常量时，应按数据角色与生命周期选择恰当的语言结构：

- **类型选择：** 有身份和生命周期的概念用 `class`；按值相等的数据用 `record`；小型（通常 16 字节以内）且不可变的值用 `readonly struct` 或 `readonly record struct`。
- **继承与密封：** 开放多态用 `interface` 表达；共享实现或受保护状态时才用 `abstract class`；不打算被继承的类宜声明为 `sealed`。
- **不可变与初始化：** 数据类型用 `init` 访问器或 `record` 位置参数；通过对象初始化器赋值的必传成员应声明 `required`（C# 11+），不应用无业务含义的空字符串或 `default!` 掩盖未初始化状态；公开集合宜以 `IReadOnlyList<T>`、`IReadOnlyDictionary<TKey, TValue>` 暴露。
- **常量与闭合变体：** 编译期常量用 `const`，运行期确定或跨程序集公开的可变化值用 `static readonly`；纯标签有限类别用 `enum`，闭合变体携带不同数据时用 `abstract record` 加 `sealed record` 派生。
