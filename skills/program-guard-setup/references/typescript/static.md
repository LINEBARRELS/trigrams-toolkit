# TypeScript / JavaScript 强可转化原则（static）

下列 principle 的核心条款可直接转化为 TypeScript 编译器、ESLint / Biome 与架构依赖工具的确定性检查。实际配置前，通过 `handbook load` 读取对应正文核对例外条件。

## `core:principle:programming-code-metrics/review-code-size-and-nesting`

- **验证工具**：ESLint（或等效 AST 指标规则）。
- **映射方向**：
  - 声明参数上限 → `max-params`。
  - 手写源文件物理行上限 → `max-lines`（排除生成目录与快照映射文件）。
  - 函数有效行上限 → `max-lines-per-function`（启用跳过空行与注释选项；注意默认口径含纯括号行，与 `narrow-ts-types-and-exhaust-discriminated-unions` 对齐）。
  - 控制流嵌套深度上限 → `max-depth`。
- **档位参数**：按用户选定档位填入 `personal` / `small` / `medium`（默认）/ `large` 对应数值；机器生成代码、测试夹具与纯数据表通过 `ignores` 豁免。

## `core:principle:programming-typescript-javascript/narrow-ts-types-and-exhaust-discriminated-unions`

- **验证工具**：TypeScript (`tsc`) + `typescript-eslint`（需开启类型感知 Lint）。
- **映射方向**：
  - 严格类型与控制流收窄 → `tsconfig.json` 开启 `strict: true`（按需补 `noUncheckedIndexedAccess`、`exactOptionalPropertyTypes`）。
  - 禁用 `any` 与非空断言 `!` → `typescript-eslint` 的 `no-explicit-any`、`no-non-null-assertion`。
  - 限制危险类型断言与双重断言 → `consistent-type-assertions`、`no-unsafe-type-assertion`（按当前安装版本核验可用规则名），引导使用类型谓词（`x is T`）或断言函数完成复杂收窄。
  - 可辨识联合 `switch` 穷尽检查 → `switch-exhaustiveness-check`，配合源码默认分支的 `never` 赋值。

## `core:principle:programming-design-module/keep-module-dependencies-acyclic`

- **验证工具**：`dependency-cruiser`（推荐，全图分析速度快）或 ESLint `import/no-cycle`。
- **映射方向**：
  - 优先依据 `docs/ARD.md` 的模块划分或既有目录边界配置 `dependency-cruiser` 的 `no-circular` 规则，阻断跨模块循环依赖（按模块目录例外配置，不误伤单模块内部互引用）。
- **注意**：动态事件总线或反射隐藏的运行期环无法被静态依赖图捕获，仍需在 Review 时排查。

## `core:principle:programming-design-architecture/point-dependencies-inward-toward-business-decisions`

- **验证工具**：`dependency-cruiser` 或 `eslint-plugin-boundaries`。
- **映射方向**：
  - 优先依据 `DEVTECH.md`（“应用架构”）与 `docs/ARD.md` 识别各架构层及模块对应的目录或工作区包，尚无架构文档时按实际代码结构识别。
  - 按允许依赖方向配置导入约束：禁止核心领域与编排目录 `import` 外层框架、UI、存储、网络与具体第三方 SDK，守住依赖倒置与组合根装配边界。

## `core:principle:programming-design-repo/name-shared-code-by-domain-knowledge`

- **验证工具**：`dependency-cruiser` 或 ESLint 文件／目录命名规则（或轻量化 CI 路径检查脚本）。
- **映射方向**：
  - 拦截新增的 `utils`、`helpers`、`common`、`misc` 等泛化杂物间目录或文件名。
  - 存量项目已有历史 `utils/` 目录时，通过豁免列表冻结既有路径，仅阻止继续新建同类文件与目录。
