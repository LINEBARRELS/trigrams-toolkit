---
description: 划分源文件职责边界、命名文件或分离模块公开入口时使用（repo.file-per-concept）。
---
# Keep One Primary Concept per File

- **Goal:** Let readers locate concepts by filename and understand each file as a coherent whole.
- **Procedure:**
  1. Put one concept in each file: one primary type, or a group of small types and functions that collaborate closely and change together.
  2. Name the file after its primary concept.
  3. Store a module's public entry points separately from its internal implementation so that the parts available to external code are immediately apparent.
  4. If a file is expected to exceed the line limit in the language-specific coding guidelines, split it by responsibility, not by line count.
- **Exceptions:** Generated code, pure data tables, and groups of related small types declared together according to language conventions.
