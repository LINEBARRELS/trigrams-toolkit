---
description: 在 TypeScript／JavaScript 中建模互斥状态、领域 ID、有限字面量或只读数据结构时使用。
---
# 使用可辨识联合与品牌类型建模 TypeScript 状态

声明 TypeScript／JavaScript 类型、状态模型与数据字段时，应利用类型系统消除非法状态组合：

- **互斥状态：** 互斥状态应使用可辨识联合（Discriminated Unions）表达，不应用多个布尔字段组合，避免出现非法状态组合。
- **领域原始值：** 底层类型相同但业务含义不同的值（如不同实体的 ID）宜用品牌类型区分：`type UserId = string & { readonly __brand: "UserId" }`。
- **有限取值：** 有限取值宜用字符串字面量联合或 `as const` 对象表达；项目已使用 `enum` 时沿用既有约定。
- **只读与抽象：** 数据类型的字段宜标 `readonly`，数组用 `readonly T[]`（注意 `readonly` 与 `Readonly<T>` 仅作用于浅层）；多态优先用 `interface` 或函数类型表达，`class` 用于有内部状态且需维护不变量的对象。
