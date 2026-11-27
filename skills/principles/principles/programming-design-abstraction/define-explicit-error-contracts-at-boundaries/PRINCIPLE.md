---
description: 定义公开操作可能怎样失败，以及调用方如何区分和处理各类失败时使用。
---
# Define Explicit Error Contracts at Boundaries

- **Goal:** Let callers determine how an operation can fail from its signature and handle failure accordingly.
- **Procedure:**
  1. Define failure semantics for every public operation. Represent expected failures (not found, validation failure) through return values, using nullable types, result types, or the Try pattern. Throw exceptions for precondition violations or situations in which execution cannot continue.
  2. Use the same representation for the same category of failure within a module.
  3. Define exception types according to how callers handle them: failures handled in the same way share a type; failures requiring different handling use different types.
  4. Fail immediately on impossible states instead of masking them with default values.
