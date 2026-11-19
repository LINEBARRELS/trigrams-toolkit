---
description: 面对相似代码判断是否提取公共函数、类型或常量时使用（abstraction.knowledge-not-shape）。
---
# Extract Shared Knowledge, Not Coincidental Shape

- **Goal:** Give each piece of business knowledge a single authoritative source; do not force code together merely because it happens to look similar.
- **Procedure:**
  1. When two pieces of code look similar, ask: "If the rule changes, must both pieces change together?"
  2. If they must, they represent the same knowledge. Extract it into a function, type, or constant named after that knowledge, and reference it from both places.
  3. If they need not change together, the similarity is only superficial. Keep them separate, even if the code is duplicated.
  4. If you cannot tell, wait for a third occurrence before deciding.
- **Exceptions:** Duplicate validation on both sides of a platform boundary, such as the client and server, may remain if a separate single source of definition exists.
