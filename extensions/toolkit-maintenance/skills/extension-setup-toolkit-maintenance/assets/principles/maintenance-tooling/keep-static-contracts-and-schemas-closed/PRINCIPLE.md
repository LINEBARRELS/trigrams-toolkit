---
description: 修改公共 CLI 命令目录、JSON Schema、随包资源或仓库静态校验规则时使用。
---
# 保持静态契约、Schema 与打包边界闭包完整

公共 CLI 协议、JSON Schema、随包资源与打包声明共同构成静态契约闭环，任意一侧变更均应同步维护其余关联方，不应只改代码或只改文档。

维护工具契约与校验边界时应满足以下要求：
- 变更 `src/trigrams_toolkit/resources/` 下的协议与 JSON Schema 时，保证全部 `$id` 唯一、本地 `$ref` 闭包完整，且命令声明与实际 CLI 子命令及参数语义一致。
- 变更随包交付的资源或模板时，核对 Python 发行包打包清单与运行时访问边界，避免遗漏交付文件或引入包外路径依赖。
- 变更后应实跑 `scripts/check_protocols.py`、相关单测及适用时的 `scripts/check_package.py`，以实测退出码与 JSON 结果作为闭环依据。
