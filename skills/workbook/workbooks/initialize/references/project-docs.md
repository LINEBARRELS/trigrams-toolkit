# 基础文档与目录

按用户描述与项目事实填写；信息缺失影响产品方向时询问用户，不为填满模板编造设计。动笔编辑文档前使用 `doc-polish`。

## 基础文档与配置

| 文档 / 配置 | 模板 | 内容 |
| --- | --- | --- |
| PRODUCT | [PRODUCT](../assets/templates/PRODUCT.md) | 产品定位、目标用户、场景、价值、已确定范围和全局业务术语 |
| DEVTECH | [DEVTECH](../assets/templates/DEVTECH.md) | 已选技术、工程组织、宏观职责、约束和全局技术术语 |
| AGENTS | [AGENTS](../assets/templates/AGENTS.md) | 项目事实、目录导航、开发命令和关键约束（含项目术语检索） |
| DESIGN | [DESIGN](../assets/templates/DESIGN.md) | 已确定的视觉与交互方向 |
| ARD | 无独立模板 | 已确定的架构边界与 Module / Feature 结构 |

core 文档与目录的路径、用途和读取时机见 [AGENTS](../assets/templates/AGENTS.md) 模板的“项目结构”；扩展专属条目由项目已安装的 `extension-setup-<extension>` 维护，读取时机与来源见[主 workbook](../WORKBOOK.md#必要工作流程)。按选定范围创建文档，内容缺失时保留必要标题与待确认事实。迁移项目按已确认清单保留有效正文，或从归档原件生成标准成果；身份按成果是否延续判定。

- **PRODUCT**：从“产品定位”开始填写，按需整理跨功能或跨玩法通用的“核心术语”。
- **DEVTECH**：保留“技术栈与工程组织”和“应用架构” 2 项基础内容。按需补充跨模块通用的“核心术语”，只写已确定的宏观约束。代码尚未建立时，在本文件记录工程目录、命令和基础设施规划。
- **DESIGN**：沿用模板标准二级标题的英文名称与顺序，正文使用用户语言，不适用章节可省略；色彩、字体和组件值未确定时不填假数据，`frontmatter` 中的 `tokens` 与正文保持一致（模板依据 Google Labs DESIGN.md alpha 格式，2026 年 10 月 8 日核对；更新格式时核对官方规范）。

填写后删除各文档的模板注释和不适用的空章节。

## 目录与 AGENTS.md 装配

按已确定内容和后续工作建立实际使用的目录（空目录可放 `.gitkeep`），源码、测试、资源和自有工具目录只创建已确定部分。在项目根置入 [.gitignore](../assets/templates/.gitignore)、[.ignore](../assets/templates/.ignore) 与 [.rgignore](../assets/templates/.rgignore)（已有对应文件时合并过滤规则），隔离运行锁、回滚日志、构建缓存、测试快照、历史计划、媒体资源与测试夹具。

- **全新项目**：完成所选材料、目录与基础文档后装配根 `AGENTS.md`。
- **迁移项目**：进入执行阶段后，先按清单保存旧入口原件，再按目标结构启用新根 `AGENTS.md`。迁移期入口保留有效项目约束与真实工程事实，链接 `migration/` 清单；可列出已确认的待生成路径，并注明“导航为目标结构，生成进度与旧资料位置见迁移清单”。验收时删除该说明与临时链接，收敛为实际结构。

根 `AGENTS.md` 按以下规则装配：

1. 采用基础模板的 core 条目，将已启用扩展的条目合入同一组表格，不加“适用条件”列或扩展判断提示；未启用或移除扩展时，删去对应的专属导航（不因此删除已有文档）。
2. 未安装的目录不列入最终导航。公共工具使用全局命令，不在项目创建私有工具目录。创建或合并根 `AGENTS.md` 时，原样保留模板“公共工具与项目配置”章节中的固定文案，置于命令表前。
3. 补充项目专项文档和已存在的工程目录，按路径更新已有条目并合并重复内容。最终导航只记录实际存在的路径（可用 Markdown 链接）。
4. 填写项目概况、开发命令与关键约束：
   - **开发命令：** 注明用途、运行目录与前提，仅实际执行成功的标为已验证。
   - **项目术语：** 按实际启用的文档路径装配检索说明，归拢跨界术语。
   - **项目规则：** 合入旧入口中无冲突的有效规则；冲突项待用户确认方案后补入。
   - **身份约束：** 若项目使用正式成果或架构实体 ID，合入以下约束并沿用已有同义规则：移动、重命名和修改内容时保留已有 ID；新增实体使用新 ID，复制文档时不复用原 ID。
   - **清理核对：** 删除模板注释与空章节，逐项核对导航与实际文件、目录一致。

`AGENTS.md` 不承载 Skill 清单、调用路由、安装记录或用户全局配置。使用 Claude 时，在根目录 `CLAUDE.md` 中引用 `AGENTS.md`，并保留项目原有的 Claude 规则。

## 项目资源与验证

首次添加项目自建 workbook 时，编写唯一入口 `WORKBOOK.md`（在 YAML 头声明 `name`、`description` 及必要的 `includes`），并在 `docs/resources.json` 中声明 `project` 来源并将 `"workbooks"` 加入 `resourceRoots`（已有声明时保留有效字段与资源根，尚无自建资源时不必创建空声明清单）。

项目 principle 通过 `principle-maintenance` 在 `docs/research/principle-drafts/` 提炼草稿，经用户审定后通过 `handbook import-principle` 入库至 `docs/knowledge/principles/<scope>/<name>/PRINCIPLE.md`，CLI 自动维护项目原则资源声明。

在项目根运行 `handbook validate` 确认项目资料来源通过校验，并用 `handbook list` 与 `handbook load` 核对自建资料可正常发现与加载。workbook 按 `meta` 演练代表性工作，principle 按 `principle-maintenance` 审定并核对影响；格式校验不能代替实际演练。
