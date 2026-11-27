---
description: 编写 UI 绑定、引擎回调或 I/O 等难测运行时边界代码时使用。
---
# Keep Business Rules Out of Runtime Adapters

- **Goal:** Limit hard-to-test code to transferring data and delegating calls; keep all decision logic in code that can be tested independently.
- **Procedure:**
  1. Identify code that requires its runtime environment to execute: UI bindings, engine lifecycle callbacks, hardware access, and network and file I/O.
  2. Limit these locations to three tasks: converting external input into internal data, calling orchestration or decision logic, and passing results back to the external environment.
  3. Move any business conditionals or calculations found there into decision logic, and invoke that logic from the boundary.
- **Exceptions:** Branches concerned solely with the external protocol itself, such as mapping HTTP status codes to errors, may remain at the boundary.
