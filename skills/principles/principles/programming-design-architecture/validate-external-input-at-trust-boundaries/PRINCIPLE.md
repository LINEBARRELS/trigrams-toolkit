---
description: 接收外部请求、文件或服务数据时，确定校验位置以及内部代码可以依赖的约束。
---
# Validate External Input at Trust Boundaries

At each trust boundary, validate the incoming data's shape and the constraints the receiving side relies on. Convert accepted input into internal values and report malformed input through the boundary's failure contract.

Internal consumers can rely on guarantees established at entry while those guarantees hold. Check conditions that depend on current state when the operation uses that state. For example, parsing an order ID establishes its format. Looking up the order establishes whether it exists.
