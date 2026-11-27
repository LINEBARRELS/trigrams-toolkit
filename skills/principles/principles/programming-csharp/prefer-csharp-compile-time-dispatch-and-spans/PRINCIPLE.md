---
description: 在 C# 中实现泛型按类型分派、外部标识多态路由、序列化正则元编程或高频连续切片解析时使用。
---
# 优先采用 C# 编译期静态契约与零拷贝切片

实现泛型按类型分派、多态装配与高频切片解析时，应使用编译期契约与切片视图替代运行期分支、反射与拷贝：

- **静态抽象泛型契约：** 泛型中按类型解析、构造或运算时，应使用 C# 11+ 接口 `static abstract` 成员约束（优先复用 `IParsable<TSelf>`、`ISpanParsable<TSelf>`、`INumber<TSelf>`），不应在泛型体内编写 `typeof(T) == ...` 分支或装箱强转。
- **开放变体边界查表：** 将外部配置标识映射到开放接口多态时，应在组合根收集 `IEnumerable<T>` 构建 `FrozenDictionary`（或键值注入）完成单次路由，不应在单一类型内持字符串标签编写过程式分支。
- **编译期元编程：** 常规业务分派与映射不应使用 `dynamic` 或运行期反射绕过类型检查；序列化与正则优先采用 Source Generator（如 `[JsonSerializable]`、`[GeneratedRegex]`）。
- **连续内存切片：** 高频字符串切分、协议解析与缓冲区读取优先使用 `ReadOnlySpan<T>`／`ReadOnlyMemory<T>`，避免重复分配子串或中间数组。
