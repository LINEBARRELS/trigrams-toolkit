---
description: 管理可变状态、共享资源释放生命周期或并发同步策略时使用。
---
# Assign a Single Owner to Mutable State

- **Goal:** Make the source of every change to mutable state traceable.
- **Procedure:**
  1. Assign a single owner to each piece of mutable state. Only the owner may modify it; other code reads and writes through the owner's operations.
  2. Do not introduce writable global variables, singletons with writable fields, or module-level mutable state. When state must be shared, create it in the composition root and pass it to its consumers.
  3. Assign owners to resources (files, connections, event subscriptions, background tasks) as well. The owner is responsible for releasing or stopping them.
  4. When multiple threads or coroutines access the same state, choose the synchronization approach during design: read-only sharing, message passing, or locking managed by the owner.
- **Exceptions:** Process-wide constants, configuration that is read-only after startup, and log output.
