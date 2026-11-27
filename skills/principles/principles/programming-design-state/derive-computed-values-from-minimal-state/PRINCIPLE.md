---
description: 判断是否新增可变状态字段、区分权威状态与可计算派生值或保留历史事实快照时使用。
---
# Derive Computed Values from Minimal State

- **Goal:** Store only canonical state and historical facts, computing derived values on demand to avoid synchronization bugs.
- **Procedure:**
  1. Before adding a mutable state field, ask whether its value can be computed from state that already exists.
  2. Do not store values that are projections of current state, such as a list's count alongside the list, a selected object copy alongside its selected ID, or filtered and formatted views. Compute them in functions, getters, or read-only memoized selectors.
  3. Never maintain multiple mutable sources of truth that require callbacks, watchers, or effects to stay in sync.
  4. Retain a separate field when the value records an immutable historical fact at a point in time, such as the price captured when an order was placed rather than the product's current price.
- **Exceptions:** Materialized caches or indexes proven necessary by profiling, provided they are encapsulated behind a single owner and invalidated atomically on write.
