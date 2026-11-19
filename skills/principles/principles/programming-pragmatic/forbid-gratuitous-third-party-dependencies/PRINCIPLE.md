---
description: 评估是否引入外部第三方依赖包时使用（pragmatic.no-gratuitous-deps）。
---
# Forbid Gratuitous Third-Party Dependencies

- **Goal:** Protect project supply chain and maintenance health by forbidding external dependency additions for trivial tasks.
- **Procedure:**
  1. Do not install a new third-party dependency for utilities that can be implemented cleanly with standard libraries or a few dozen lines of code.
  2. Before proposing a new dependency, assess: license compatibility, maintenance status, transitively installed packages, bundle/binary size impact, and whether the project already has an alternative that covers 80% of the need.
  3. If a dependency is approved, wrap it at the boundary per `abstraction.foreign-wrap` to prevent vendor lock-in.
- **Exceptions:** Substantial domain algorithms, cryptographic implementations, official hardware/SDK drivers, and foundational infrastructure frameworks.
