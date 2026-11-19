---
description: 按需求变化来源划分或合并模块职责时使用（module.change-axis）。
---
# Split Modules by Stakeholder Change Axis

- **Goal:** Change a module only in response to requirements from a single stakeholder group.
- **Procedure:**
  1. For each candidate module, list the stakeholders whose requirements could cause it to change, such as those responsible for gameplay design, UI design, save formats, or network protocols.
  2. If more than one stakeholder group is involved, split the module by stakeholder group.
  3. If two candidate modules always change together in response to the same requirement from the same stakeholder group, merge them (see `module.common-closure`).
  4. Execution order alone is not a reason to separate two pieces of code into different modules.
- **Exceptions:** The composition root accommodates multiple stakeholder groups by design, but it should contain no business rules.
