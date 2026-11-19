---
description: 设计模块调用方式、收拢内部算法格式或消除固定调用顺序时使用（abstraction.deep-module）。
---
# Hide Decision Complexity Inside Deep Modules

- **Goal:** Let callers accomplish their work with little knowledge of the module, keeping complexity inside it.
- **Procedure:**
  1. Describe the module's usage from the caller's perspective: which operations, parameters, and call sequences must the caller know?
  2. If callers must retrieve data and then make decisions themselves, move those decisions into the module that owns the data, leaving callers to issue commands. For example, call `inventory.TryConsume(item)` instead of retrieving a quantity, comparing it, and writing it back.
  3. Keep formats, algorithms, storage layout, and caching under the module's control and out of public signatures.
  4. If callers must invoke several operations in a fixed order to obtain a correct result, combine them into one operation or enforce the call order through types.
- **Exceptions:** Formatting and serialization code exists to produce representations of data from other types.
