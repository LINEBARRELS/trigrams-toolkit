---
description: 选择模块内部划分、接口抽象或独立组件等隔离机制时使用。
---
# Match Boundary Cost to Isolation Need

- **Goal:** Keep a boundary's cost proportional to the isolation it provides.
- **Procedure:**
  1. From lightest to heaviest, boundary mechanisms are: grouping functions within a module; separating a module's public and internal members; introducing an interface and its implementation; and using a separate assembly, package, or process.
  2. Default to the lightest mechanism that meets the current isolation requirements.
  3. Introduce an interface when any of the following holds: a second implementation already exists; tests need to substitute the dependency; or business code needs to call an external capability through a contract it owns.
  4. Introduce a separate component when independent release or deployment is required, or when dependencies in the reverse direction must be prohibited at compile time.
- **Exceptions:** Design published public APIs and plugin interfaces according to their external contracts.
