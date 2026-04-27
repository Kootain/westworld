# Tasks
- [x] Task 1: 基础构建 - 实现 core 模块及测试
  - 任务描述：读取 `docs/design/core-module.md`，实现 `src/core/` 目录下的代码（枚举、数据模型、配置等）。编写 `tests/test_core.py` 并保证测试通过。完成后总结实现过程中的反思，并追加到 `docs/design/core-module.md` 的末尾。
- [x] Task 2: 存储与 I/O 层 - 实现 io 和 memory 模块及测试
  - 任务描述：读取 `docs/design/io-module.md` 和 `docs/design/memory-module.md`，实现 `src/io/` 和 `src/memory/` 目录下的代码。编写相关的单元测试 (`tests/test_io.py`, `tests/test_memory.py`)。完成后总结实现反思，并分别追加到这两个设计文档的末尾。
- [x] Task 3: 认知与容器层 - 实现 agent 和 box 模块及测试
  - 任务描述：读取 `docs/design/agent-module.md` 和 `docs/design/box-module.md`，参考前序模块的设计和代码，实现 `src/agent/` 和 `src/box/` 目录下的代码。编写相关的单元测试 (`tests/test_agent.py`, `tests/test_box.py`)。完成后总结实现反思，追加到对应的设计文档中。
- [x] Task 4: 编排层 - 实现 graph 模块及测试
  - 任务描述：读取 `docs/design/graph-module.md`，参考所有前置模块的设计与代码，实现 `src/graph/` 目录下的代码（LangGraph 工作流编排）。编写测试 (`tests/test_graph.py`)。完成后总结实现反思，追加到设计文档中。

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 1, Task 2
- Task 4 依赖于 Task 1, Task 2, Task 3
