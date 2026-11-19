---
description: 判断是否引入接口、基类、泛型参数或配置开关时使用（abstraction.earned）。
---
# Earn Abstractions from Real Variants

- **Goal:** Give every abstraction a responsibility that already exists.
- **Procedure:**
  1. Before adding an interface, base class, generic type parameter, strategy extension point, or configuration toggle, confirm that it satisfies at least one of the following:
     - The current design already has at least two real variants.
     - It isolates an external dependency that is known to change or need replacement.
     - It maintains an invariant that callers should not have to maintain themselves.
     - It hides complex details that callers do not need to know.
  2. If none applies, write a concrete implementation. Extract the abstraction when a second variant appears.
  3. Do not introduce a wrapper layer that only forwards calls without adding validation, composition, or transformation.
- **Exceptions:** Published public APIs and extension points already used by external plugins.
