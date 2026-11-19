---
description: 平衡系统信任边界的严格校验与内部实现的极简表达时使用（pragmatic.asymmetric-rigor）。
---
# Enforce Strict Boundaries with Lightweight Internals

- **Goal:** Combine extreme minimalism in internal implementation with uncompromising rigor at system boundaries and error handling.
- **Procedure:**
  1. Maintain strict rigor at trust boundaries: validate external inputs, enforce domain invariants, verify authentication/authorization, and handle potential null/empty or malformed states completely.
  2. Guard against data loss, concurrency races, and resource leaks with fail-fast validation and explicit error contracts.
  3. Conversely, be ruthlessly pragmatic and lightweight inside internal implementation: avoid gratuitous wrappers, deep inheritance hierarchies, and redundant internal validations.
  4. Never compromise security, correctness, or error visibility under the guise of "writing less code."
- **Exceptions:** High-performance internal loops where pre-validated data can bypass redundant intermediate assertions.
