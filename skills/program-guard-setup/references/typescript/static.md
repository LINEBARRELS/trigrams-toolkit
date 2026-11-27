# TypeScript / JavaScript 强可转化原则（static）

下列 principle 的核心条款可直接转化为 TypeScript 编译器、ESLint / Biome 与架构依赖工具的确定性检查。实际配置前，通过 `handbook load` 读取对应正文核对例外条件。

## `core:principle:programming-scale/keep-code-within-scale-limits`

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
  - 禁止跨模块循环依赖 → `dependency-cruiser` 启用 `no-circular` 规则（模块内类型互引用按目录边界例外配置，不误伤单模块内部）。
- **注意**：动态事件总线或反射隐藏的运行期环无法被静态依赖图捕获，仍需在 Review 时排查。

## `core:principle:programming-design-architecture/point-dependencies-inward-toward-business-decisions`

- **验证工具**：`dependency-cruiser` 或 `eslint-plugin-boundaries`。
- **映射方向**：
  - 需先识别项目分层目录（如 `domain/`、`application/`、`infrastructure/`、`ui/`）。
  - 为内层业务目录配置禁止规则：禁止 `import` 外层框架、UI、存储、网络与具体第三方 SDK 路径，仅允许依赖语言标准库与内层领域类型。

## `core:principle:programming-design-repo/name-shared-code-by-domain-knowledge`

- **验证工具**：`dependency-cruiser` 或 ESLint 文件／目录命名规则（或轻量化 CI 路径检查脚本）。
- **映射方向**：
  - 拦截新增的 `utils`、`helpers`、`common`、`misc` 等泛化杂物间目录或文件名。
  - 存量项目已有历史 `utils/` 目录时，通过豁免列表冻结既有路径，仅阻止继续新建同类文件与目录。
