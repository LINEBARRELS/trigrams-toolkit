# 架构可视化报告通用指引

## 前置准备

- 使用 `principles` skill，读取 `programming-review` scope 下的全部原则。
- 读取派发提供的维护后文档与必要引用；制作 ARD 报告时可读取项目 DEVTECH。

## 事实边界与审查要求

- 仅依据维护后的文档和必要引用文档绘图，检查设计中的结构、关系与行为是否清楚、自洽。
- 汇报目标为忠实呈现当前设计文档内容，不读取 `answer-me-with-html` 的 `references/codebase.md`，也不借用工程代码补写或调整设计事实。
- 在报告中标明缺失或矛盾之处、对应章节与待确认问题；待用户裁决的问题可使用 `ask` 组件供页面内勾选回复。

## 渲染与交付

- 使用 `answer-me-with-html` Skill 生成单页 HTML 报告，按对应专项指引组织图表与版面。
- 渲染时附加 `--no-open`，并通过 `-o` 将成品写入项目根 `.tmp/answer-me/` 下各自的报告路径。
- 向主 Agent 返回 HTML 成品路径及必要核对摘要。
