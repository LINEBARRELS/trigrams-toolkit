---
description: 评估需求变更影响范围并收拢同类业务知识时使用（module.common-closure）。
---
# Confine Requirement Changes to One Module

- **Goal:** Confine each requirement change to one module.
- **Procedure:**
  1. List several foreseeable requirement changes for the candidate design, such as adding an item type, adjusting scoring rules, or changing the save format. Use these changes only to evaluate the structure; do not implement the features in advance.
  2. Count the modules that each change would affect. When one change affects multiple modules, check whether those locations express the same knowledge. If they do, consolidate that knowledge in one module.
  3. Keep a rule's constants, validation, and calculations in the same module, and have other modules call it.
- **Exceptions:** Shared type definitions can keep protocol fields consistent across modules without merging the modules.
