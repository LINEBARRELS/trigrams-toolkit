---
description: 验收 arch 框架产出或审查代码结构，排查纯转发包装层、无真实变体的假扩展点与无主死代码等冗余设计时使用（review.no-surplus）。
---
# Eliminate Surplus Indirection

- **Goal:** Reject structural layers, abstractions, and declarations that have no independent reason of their own to change.
- **Procedure:**
  1. Reject pass-through wrappers, middle-man classes, and forwarding interfaces that only delegate calls without enforcing an invariant, translating a boundary, or hiding complexity.
  2. Reject speculative generality: single-implementation interfaces, unused generic parameters, strategy hooks, or configuration flags built for hypothetical future needs without a real second variant or external boundary.
  3. Reject unreferenced types, dead branches, placeholder parameters, and comments that merely restate the signature or implementation.
- **Exceptions:** Published public APIs, external plugin contracts, and thin boundary interfaces required to invert dependencies toward business decisions.
