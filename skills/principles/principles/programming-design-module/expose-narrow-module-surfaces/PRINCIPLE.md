---
description: 设计模块公开接口、按调用方拆分接口或隐藏内部数据结构时使用。
---
# Expose Narrow Module Surfaces

- **Goal:** Make callers depend only on the capabilities they use, leaving module internals free to change.
- **Procedure:**
  1. List each module's callers and the operations each caller uses.
  2. Expose only the operations and types callers use; keep the rest internal or private.
  3. When different callers use largely non-overlapping sets of operations, split the interface by caller.
  4. Return values from public operations must not expose internal data structures. Callers should not traverse successive layers of returned objects to retrieve values.
- **Exceptions:** Design a general-purpose library's public API for its intended users; do not trim it to the callers currently present in the repository.
