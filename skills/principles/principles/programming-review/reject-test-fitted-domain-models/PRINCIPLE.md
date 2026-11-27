---
description: 审查代码结构，排查面向验收样例焊死步骤基数、硬编码测试夹具常量或残留测试假实现等退化建模时使用（review.no-test-fitting）。
---
# Reject Test-Fitted Domain Models

- **Goal:** Model real domain invariants rather than overfitting acceptance probes.
- **Procedure:**
  1. Reject schemas, types, or state machines hardcoding sample counts or fixed slots (e.g., `step1`/`step2`) for open sequences.
  2. Reject production logic baking in fixture IDs, probe literals, or synthetic fallbacks just to pass a test.
  3. Reject test doubles, `fake` adapters, or debug bypasses left inside production modules.
  4. Distinguish simplicity from degradation: omitting unrequested scope is valid; collapsing a general contract into a single-case script is not.
- **Exceptions:** Test suites, fixture packages, and fixed-cardinality protocols.
