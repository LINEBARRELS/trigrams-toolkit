---
name: 工具包扩展开发与维护
description: 新建工具包扩展，或对已有扩展（含清单、Setup 入口、workbook、principle、领域 Skill 与说明文稿）执行重构、迁移或结构合规核验。
resourceId: toolkit-maintenance:workbook:maintenance-extension
includes:
- toolkit-maintenance:principle:maintenance/keep-one-authoritative-source-per-rule
- toolkit-maintenance:principle:maintenance/keep-reference-chains-reachable-and-complete
- toolkit-maintenance:principle:maintenance-extension/keep-extension-self-contained-in-setup-assets
---

# 工具包扩展开发与维护

## 适用与输入

明确工作目标（新建、重构演进、身份或版本迁移、结构合规核验）、目标扩展标识、维护源路径、代表性使用场景及受影响的制品集合。维护已有扩展时，补充当前 `extension.json`、仓库 `toolkit.json` 登记、关联测试及项目已安装快照现状。领域边界或公共契约未定时，先反馈设计问题。

## 必要工作流程

<schedule-rule>
按本次工作类型确定推进方向与验收重点（派发执行时可按需随附参考）：

| 工作类型 | 方法与验收重点 |
| --- | --- |
| 新建扩展 | 先确认与 core 的正交边界与领域契约，再搭建 `extension-setup-<name>` 与 `assets/` 资源，通过源仓库校验与安装快照实测 |
| 重构与演进 | 先盘点受影响的 `resourceId`、跨文件引用、关联测试与使用方，按唯一维护源同步修改并清理退役资产 |
| 身份或版本迁移 | 以显式 `resourceId` 或同步索引维持现行引用可达，更新 `toolkit.json` 与版本声明，并核验快照刷新结果 |
| 结构合规核验 | 执行完整六维扩展结构预期检查与工具链实测，输出可复现的逐项证据（只读核验不修改源码） |

跨能力协同：涉及 `src/trigrams_toolkit/` 或 `tests/` 的 Python 源码重构时，衔接 `core:workbook:programming-development` 并按需加载 `core:principle:programming*`；涉及目标项目底座集成验证时，对照 `core:workbook:project-setup`；中文文稿遵循 `doc-polish`。
</schedule-rule>

<exec-rule>
按以下顺序推进扩展开发、维护或核验（只读结构合规核验跳过第 3 步写操作）：

1. 界定边界与架构：按需从 `maintenance-extension` 加载原则，确认扩展职责边界、`<ext>:*` 命名空间隔离及与 core 的正交关系。
2. 盘点影响面：从变更点定位受影响的 `toolkit.json`、`assets/extension.json`、`extension-setup-<name>/SKILL.md`、`agents/openai.yaml`、`workbooks/`、`principles/`、领域 `SKILL.md`、`README.md` 及关联测试。
3. 按材料类型加载原则并修改唯一维护源：
   - 扩展清单、Setup 入口与快照边界：从 `maintenance-extension` 按需加载；
   - 原则新增、拆分、压缩、命名与身份变更：从 `maintenance-knowledge` 按需加载；
   - 工作方法结构、规则槽位与工序切分：从 `maintenance-workbook` 按需加载；
   - Skill 类型、内聚边界与文档生命周期：从 `maintenance-skill` 按需加载；
   - 公共 CLI、私有脚本、静态契约与 Schema：从 `maintenance-tooling` 按需加载；
   - 规则分层、公开契约暴露与正向表述：从 `maintenance` 按需加载；
   - Python 源码与测试改动：按需加载 `core:principle:programming*`。
4. 执行“扩展结构预期检查”硬性核心流程（逐项落实，发现不符应修复或明确标定阻断，不应跳过）：

| 检查维度 | 硬性检查动作 | 对应原则 / 验证入口 |
| --- | --- | --- |
| 1. 仓库登记与包边界 | 核对 `toolkit.json` 指向唯一包根 `assets/`，无散落清单、生成物缓存或退役打包物 | `maintenance-extension/keep-extension-self-contained-in-setup-assets`、`scripts/verify_toolkit.py` |
| 2. Setup 入口契约 | 核对 `extension-setup-<name>/SKILL.md` 四段正交结构、`disable-model-invocation: true` 及 `agents/openai.yaml` | `maintenance-extension/structure-extension-setup-as-orthogonal-increment`、`tests/test_toolkit_validation.py` |
| 3. 清单 Schema 与隔离 | 核对 `assets/extension.json` 符合 Schema、`<ext>:*` 前缀隔离及 `install` 安全边界 | `maintenance-extension/isolate-extension-namespace-and-manifest-contracts`、`guides.schema.json` |
| 4. 资源布局与引用闭包 | 核对 `principles/` 两级目录与纯 `description` 头、`WORKBOOK.md` 头与 `includes` 闭包、`assets/` 封闭链接及规则标签完整闭合 | `maintenance-knowledge/*`、`maintenance-workbook/*`、`maintenance/keep-reference-chains-reachable-and-complete` |
| 5. 领域 Skill 与说明对齐 | 核对扩展内全部 `skills/*/SKILL.md` 命名一致且全仓无重名，核对 `README.md` 与 Setup 列举和 `assets/` 实存一致 | `maintenance-skill/*`、实存目录比对 |
| 6. 工具链实测与快照验证 | 实跑 `PYTHONPATH=src python scripts/verify_toolkit.py`（改协议或 Schema 时加跑 `scripts/check_protocols.py`）；改 `WORKBOOK.md` 时推演一次 `agile` 与 `flow` 规则抽取及原则可达性；涉快照或发布时核对 `harness-install`、`handbook validate`/`list`/`load` 与 `tasks.py check-release` | `maintenance-extension/separate-extension-source-from-installed-snapshot`、实际命令退出码与 JSON 输出 |

5. 涉及目标项目集成时，用 `harness-install` 预览并应用装配，验证快照刷新与移除清理结果；涉及发布版本时，核对 `tasks.py check-release`。
</exec-rule>

## 工序切分与交接

按独立可验证的交付结果与契约边界划定 Stub 与交接位置，例如“扩展清单与 Setup 入口”“原则与工作方法资产”“仓库测试与说明同步”“项目快照装配验证”。

小范围维护或只读结构合规核验保持单一交付单元即可；仅在多项大范围产物存在前后置依赖时按依赖切分，不强行套用多阶段交接。

## 产出与验收

交付扩展维护源改动（只读核验交付结构检查结论）、关联文档与测试同步状态、实测校验命令与输出，以及未运行范围和原因（若有）。

<review-rule>
**独立审核：** 必读 `toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence`、`maintenance-extension` 全部 principle 及改动材料对应的 scope principle（涉及源码改动时加读 `core:principle:programming-review`）。

逐项复核以下 6 个结构预期维度与实测证据：
1. `toolkit.json` 登记、`assets/` 唯一包根及禁用产物清理情况；
2. `extension-setup-<name>/SKILL.md` 四段结构、`disable-model-invocation: true` 及 `agents/openai.yaml`；
3. `assets/extension.json` Schema、`<ext>:*` 前缀隔离及 `install` 安全边界；
4. `principles/` 两级目录与纯 `description` 头、`WORKBOOK.md` 头与 `includes` 闭包、`assets/` 封闭链接及规则标签闭合；
5. 扩展内 `SKILL.md`、`README.md`、Setup 入口与 `assets/` 实存的一致性；
6. `verify_toolkit.py`（及适用时的 `check_protocols.py`、`handbook validate`/`list`/`load`、关联单测、`tasks.py check-release`）的真实运行输出，以及 `WORKBOOK.md` 变更的场景推演证据。

任意结构违规、断链或未附可复现命令输出均不予通过。
</review-rule>
