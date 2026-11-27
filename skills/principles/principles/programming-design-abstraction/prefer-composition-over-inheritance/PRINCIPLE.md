---
description: 建模对象本质分类与状态能力装配、判断是否使用继承或组合时使用。
---
# Prefer Composition over Inheritance

- **Goal:** Model object identity with inheritance ("what it is") and assemble state and capabilities with composition ("what it has and can do"), avoiding fragile hierarchies.
- **Procedure:**
  1. Use composition to explain what an object has and can do: assemble mutable state, orthogonal capabilities, and shared implementations as separate components or functions that the host object holds or calls.
  2. Use inheritance only to explain what an object fundamentally is: a stable taxonomic relationship where the subtype can substitute for the base type everywhere without strengthening preconditions or weakening postconditions.
  3. When polymorphism is needed without shared identity, prefer interfaces, protocols, or function types over concrete base classes.
  4. A base class must neither depend on nor know about its derived classes.
- **Exceptions:** Follow framework conventions for prescribed extension mechanisms, such as subclassing engine base classes or UI controls.
