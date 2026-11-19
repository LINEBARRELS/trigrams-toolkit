# 目录与项目文档

本说明对应[主 workbook](../WORKBOOK.md#原子工作目录)的**工作 2（目录骨架搭建）**与**工作 3（项目级核心文档维护）**。动笔编辑中文文档前应使用 `doc-polish`；按用户描述与项目事实填写，不为填满模板编造未确定设计。

## 工作 2：目录骨架搭建

核对项目 `docs/` 目录结构，按需求补齐缺失目录。需要预先占位的空目录放入 `.gitkeep`，已有目录保持原样：

| 目录 | 用途 | 预留策略 |
| --- | --- | --- |
| `docs/knowledge/decisions/` | 项目宏观决策记录与 `index.md` | 缺失时可放 `.gitkeep` 预留 |
| `docs/knowledge/retrospectives/` | 复盘与关键变更记录 | 缺失时可放 `.gitkeep` 预留 |
| `docs/plans/` | Plan 与 Task 工作目录 | 缺失时可放 `.gitkeep` 预留 |
| `docs/implementation-specs/` | 模块实现设计与契约（Implementation Spec） | 按需建立或预留 |
| `docs/research/` | 研究草稿与方案探索 | 按需建立 |
| `docs/references/` | 外部参考资料 | 按需建立 |
| `docs/archives/` | 退役资料归档 | 仅在产生归档或明确需要时建立 |

源码、测试、资源等工程目录只创建已确定部分。领域扩展专属目录留待[扩展管理](extensions.md)叠加，不在核心底座预设。

## 工作 3：项目级核心文档维护

按本次确认的范围新建或增量更新下列核心文档：

| 文档 | 默认路径 | 模板 | 维护范围 |
| --- | --- | --- | --- |
| PRODUCT | `PRODUCT.md` | [PRODUCT](../assets/templates/PRODUCT.md) | 产品定位、目标用户、场景、范围与全局业务术语 |
| DEVTECH | `DEVTECH.md` | [DEVTECH](../assets/templates/DEVTECH.md) | 已选技术、工程组织、宏观职责、约束与全局技术术语 |
| DESIGN | `DESIGN.md` | [DESIGN](../assets/templates/DESIGN.md) | 已确定的视觉与交互方向 |
| AGENTS | `AGENTS.md` | [AGENTS](../assets/templates/AGENTS.md) | 项目事实、目录导航、开发命令、关键约束与术语检索入口 |
| ARD | `docs/ARD.md` | 无 | **仅按需创建空占位文件**，不在本流程填充架构内容 |

### 文档编写要点

- **PRODUCT**：从“产品定位”起笔，按需整理跨功能通用的“核心术语”。
- **DEVTECH**：保留“技术栈与工程组织”与“应用架构”两项基础内容，按需补充跨模块“核心术语”；代码未建时标注为规划。
- **DESIGN**：沿用模板二级标题的英文名与顺序，正文使用用户语言，省略不适用章节；未确定的色彩、字体与组件值不填假数据，`frontmatter` 中的 `tokens` 与正文一致（依据 Google Labs DESIGN.md alpha 格式）。
- **ARD**：选定时仅创建空占位文件（如 `# ARD`），不展开架构拆解或实体登记。

填写完成后删除模板注释与不适用的空章节。已有文档做增量更新时，保留原有有效事实与自定义约束。

### AGENTS.md 装配与收敛规则

`AGENTS.md` 在核心文档落盘后收尾生成或增量更新：

1. **以模板为基准**：基于 [AGENTS 模板](../assets/templates/AGENTS.md)装配核心文档与路径表，保留已存在的领域扩展条目，不加“适用条件”列。
2. **仅列真实路径**：最终导航只记录项目内实际存在的文档与目录（可用 Markdown 链接）；公共工具使用全局命令，不在项目内建私有工具目录。
3. **保留固定文案**：创建或更新 `AGENTS.md` 时，原样保留模板“公共工具与项目配置”章节中的固定文案，置于命令表前。
4. **维护概况、命令与约束**：
   - **开发命令**：注明用途、运行目录与前提，仅实际执行成功的标为已验证。
   - **项目术语**：按实际启用的文档路径装配检索说明。
   - **项目规则与身份约束**：保留项目既有有效规则；若项目使用正式成果或架构实体 ID，保留“移动／重命名保留原 ID，新增用新 ID，复制不复用原 ID”约束。
5. **Claude 入口**：使用 Claude 时，在项目根 `CLAUDE.md` 中引用 `AGENTS.md`，并保留项目原有 Claude 规则。

`AGENTS.md` 不承载 Skill 清单、调用路由、安装记录或用户全局配置。
