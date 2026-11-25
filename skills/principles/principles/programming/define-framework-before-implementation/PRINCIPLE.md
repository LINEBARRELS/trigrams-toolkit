---
description: 编写、修改或重构代码时必读的原则，要求先确立代码框架与公开契约，再填充具体逻辑实现。
---
# 先确定框架再填充逻辑

In software development, you should first establish the code framework and public contracts the relevant modules before implementing the specific logic; this prevents the ad-hoc creation of interfaces while writing business logic and avoids "reinventing the wheel."

框架确立与逻辑实现应满足以下要求：
- 优先核对并复用既有代码框架与公共能力，不重复定义同责结构。
- 编写具体算法或业务逻辑前，先补齐本次所需的模块边界、类、函数签名、数据结构、常量、枚举与核心工具定义，明确职责、依赖方向、输入输出及失败语义。
- 在结构关系、命名与契约稳定后再填充具体逻辑；若实现中发现框架契约不合理，应先优化框架定义再继续实现。
