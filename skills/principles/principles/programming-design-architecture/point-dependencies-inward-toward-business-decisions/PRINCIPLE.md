---
description: 设计跨层依赖方向或定义外部能力接口时使用。
---
# Point Dependencies Inward Toward Business Decisions

- **Goal:** Allow external details to be replaced without changing business decisions.
- **Procedure:**
  1. Dependencies point from external interactions → orchestration → business decisions. All arrows point inward toward business decisions.
  2. When business code needs an external capability (such as reading saved data or sending a request), declare the required interface on the business side and name it using domain terminology. Implement it in the external interaction layer.
  3. Use business-side types for interface parameters and return values; do not expose framework or third-party types.
  4. Inspect every import/using directive in business modules. Replace references to UI, storage, networking, or framework namespaces with dependencies on the interfaces from step 2.
- **Exceptions:** Direct dependencies are allowed on the language's standard library and on frameworks the project has adopted as infrastructure and does not intend to replace, such as a game engine's math types.
