---
description: 在 Python 中声明数据模型、领域原始值、多态协议、常量枚举或穷尽模式匹配时使用。
---
# 使用显式类型建模 Python 数据与协议

声明 Python 类、数据结构、多态接口与变体分派时，应使用显式类型注解与不可变结构表达领域契约：

- **类型注解：** 公开函数和模块入口应写完整的类型注解；注解、`TypedDict` 和 `NewType` 不提供运行时校验，外部输入数据应另行校验。
- **数据类型与领域值：** 不可变记录使用 `@dataclass(frozen=True)` 或 `NamedTuple`，外部字典结构使用 `TypedDict`；同底层类型的业务值用 `NewType` 区分，带取值约束的值在 `dataclass` 的 `__post_init__` 中校验。
- **多态与边界映射：** 结构化多态使用 `Protocol`，共享实现使用 `ABC`，替换单一行为直接传入 `Callable`；外部标识映射开放变体时应在边界用字典查表路由，不应在单类内按字符串标签写过程式分支。
- **常量枚举与穷尽匹配：** 模块级常量用全大写并标注 `Final`，有限类别用 `Enum`（字符串枚举用 `StrEnum`）；对枚举或联合变体分派时，宜用 `match/case` 配合兜底分支 `typing.assert_never` 实现静态穷尽检查，复杂收窄封装为 `TypeIs`／`TypeGuard` 函数。
