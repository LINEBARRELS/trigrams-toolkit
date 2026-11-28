---
description: 划分领域模型与应用编排职责，或确定业务约束与状态转移规则归属时使用。
---
# Keep Domain Invariants in Domain Models

- **Goal:** Keep business validity rules cohesive with domain types, not scattered across orchestration.
- **Procedure:**
  1. Enforce value constraints, state transitions, and domain rules inside the domain module via validating constructors, invariant-preserving methods, or pure domain functions.
  2. Limit orchestration to loading inputs, invoking domain logic, and committing side effects; do not inspect and mutate raw domain fields externally.
  3. Pass rule context (timestamps, limits) as explicit values without injecting I/O dependencies into domain types.
- **Exceptions:** Pass-through CRUD records or DTOs with no domain invariants beyond entry validation.
