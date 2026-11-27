---
description: 检查模块依赖图或打破跨模块循环依赖时使用。
---
# Keep Module Dependencies Acyclic

- **Goal:** Allow modules to be understood, built, and tested in dependency order.
- **Procedure:**
  1. List the dependencies between modules and check for cycles.
  2. Break a cycle in one of two ways: declare an interface on one side and implement it on the other (dependency inversion), or extract the parts both sides need into a new module that both depend on.
  3. Do not hide cycles behind an event bus, a global registry, or reflection. These mechanisms merely turn compile-time cycles into runtime cycles.
- **Exceptions:** This rule does not apply to mutual references between types within the same module.
