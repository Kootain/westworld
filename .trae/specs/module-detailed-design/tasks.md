# Tasks
- [ ] Task 1: 编写整体架构与接口设计文档
  - 任务描述：根据 `docs/system-design.md`，在 `docs/design/overall-architecture.md` 中编写整体模块的职责规划和核心接口设计。
  - 要求：定义 `io`, `box`, `memory`, `agent`, `graph`, `core` 各模块的边界，以及关键接口（如 `InputAdapter`, `OutputAdapter`, 状态模型等）。
- [ ] Task 2: 编写 io 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/io-module.md` 中设计 I/O 插件适配器。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。
- [ ] Task 3: 编写 box 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/box-module.md` 中设计状态守卫、感官合成、隐私屏蔽等功能。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。
- [ ] Task 4: 编写 memory 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/memory-module.md` 中设计三级记忆架构及记忆衰减、固化机制。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。
- [ ] Task 5: 编写 agent 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/agent-module.md` 中设计感知、联想、思考、行为的认知节点逻辑。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。
- [ ] Task 6: 编写 graph 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/graph-module.md` 中设计 LangGraph 的 State 定义和图执行流。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。
- [ ] Task 7: 编写 core 模块详细设计文档
  - 任务描述：参考整体规划文档，在 `docs/design/core-module.md` 中设计全局配置、Pydantic 数据模型和工具类。详细描述方案。如果发现和最开始的整体规划相违背，需要将违背的部分，详细描述在本模块的方案文档里。

# Task Dependencies
- Task 2, Task 3, Task 4, Task 5, Task 6, Task 7 依赖于 Task 1。
