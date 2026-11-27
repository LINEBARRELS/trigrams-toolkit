---
description: 修改既有代码、控制改动波及面与保持最小完整差异时使用。
---
# Confine Edits to the Smallest Complete Change

- **Goal:** Confine every change to the smallest complete blast radius, minimizing disruption to existing callers and configurations.
- **Procedure:**
  1. Before modifying code, perform impact mapping: identify all affected callers, unit tests, configuration files, and downstream consumers.
  2. Choose the implementation with the smallest blast radius that completely satisfies the task. Prefer modifying an existing implementation in place over introducing parallel abstractions or sweeping refactorings.
  3. Keep diffs focused strictly on the assigned task. Do not touch unrelated files, reformat unchanged code, or rename working symbols out of personal aesthetic preference.
  4. Update or add unit tests that directly assert the minimal delta and prove that existing invariants remain intact.
- **Exceptions:** Explicit refactoring tasks where restructuring architecture across module boundaries is the primary deliverable.
