---
description: 验收 arch 框架产出或审查代码结构，排查跨位置同步、双真相源、隐式全局状态与时序约定等隐式耦合时使用（review.hidden-links）。
---
# Expose Hidden Change Coupling

- **Goal:** Reject structures where pieces must change together in lockstep without an explicit, compiler- or contract-visible link.
- **Procedure:**
  1. Flag parallel copies of rules, status maps, or action lists across modules where changing one silently invalidates the others.
  2. Flag redundant mutable state and dual sources of truth—such as storing both a collection and its count, or a selected ID and a copied object—that rely on manual synchronization or effects.
  3. Flag modules that communicate through hidden globals, shared mutable singletons, or unowned side-channel files instead of explicit parameters and return contracts.
  4. Flag temporal coupling where callers must know an undocumented call sequence, delay, or setup flag for an operation to work.
- **Exceptions:** Intentional platform-boundary projections (such as client and server schemas) that trace back to a single declared source of truth.
