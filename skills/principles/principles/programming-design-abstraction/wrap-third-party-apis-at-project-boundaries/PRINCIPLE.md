---
description: 在业务代码中引入或隔离第三方库接口与异常时使用。
---
# Wrap Third-Party APIs at Project Boundaries

- **Goal:** Confine the impact of third-party library changes to one module.
- **Procedure:**
  1. When a third-party API is used in multiple places, or its types would appear in business code signatures, wrap it in interfaces or types defined by the project.
  2. Expose only the operations the project uses, with project-defined types for parameters and return values.
  3. Translate third-party exceptions and error codes into the project's failure semantics in the wrapper.
- **Exceptions:** The language's standard library and foundational frameworks already adopted by the project; small utility libraries used in only one place may be called directly.
