---
description: 放置跨模块共享代码并避免创建 Utils／Helpers 杂物间时使用（repo.no-junk-drawer）。
---
# Name Shared Code by Domain Knowledge

- **Goal:** Give shared code a clear home instead of accumulating it in an ownerless catch-all.
- **Procedure:**
  1. Do not create directories, files, or types with generic names such as `Utils`, `Helpers`, `Common`, or `Misc`.
  2. Name and place shared code according to the knowledge it represents, such as `Money`, `GridMath`, or `RetryPolicy`.
  3. Keep helper code used by only one module inside that module.
- **Exceptions:** Existing directories of this kind may continue to be used, but new content should still be named after the knowledge it represents.
