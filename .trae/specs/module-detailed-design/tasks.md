# Tasks
- [x] Task 1: 编写整体架构与接口设计文档
  - 任务描述：根据 `docs/system-design.md`，在 `docs/design/overall-architecture.md` 中编写整体模块的职责规划和核心接口设计，并分析各模块的依赖关系。
  - 要求：定义 `core`, `io`, `memory`, `agent`, `box`, `graph` 各模块的边界，以及关键接口（如 `InputAdapter`, `OutputAdapter`, 状态模型等）。
- [x] Task 2: 编写 core 模块详细设计文档及反思
  - 任务描述：参考整体规划文档，在 `docs/design/core-module.md` 中设计全局配置、Pydantic 数据模型和工具类。由于 core 依赖最少，优先设计。
  - 要求：详细描述方案。如果发现和最开始的整体规划相违背，详细描述违背部分。完成后进行设计反思，记录反思结果供后续模块参考。
- [x] Task 3: 编写 io 模块详细设计文档及反思
  - 任务描述：参考整体规划文档和 core 模块的反思，在 `docs/design/io-module.md` 中设计 I/O 插件适配器。
  - 要求：详细描述方案。如果违背整体规划，记录违背部分。完成后进行设计反思，记录反思结果。
- [x] Task 4: 编写 memory 模块详细设计文档及反思
  - 任务描述：参考整体规划及之前的反思结果，在 `docs/design/memory-module.md` 中设计三级记忆架构及记忆衰减、固化机制。
  - 要求：详细描述方案。如果违背整体规划，记录违背部分。完成后进行设计反思，记录反思结果。
- [x] Task 5: 编写 agent 模块详细设计文档及反思
  - 任务描述：参考整体规划及 memory/core 等模块的反思结果，在 `docs/design/agent-module.md` 中设计感知、联想、思考、行为的认知节点逻辑。
  - 要求：详细描述方案。如果违背整体规划，记录违背部分。完成后进行设计反思，记录反思结果。
- [x] Task 6: 编写 box 模块详细设计文档及反思
  - 任务描述：参考整体规划及之前的反思结果，在 `docs/design/box-module.md` 中设计状态守卫、感官合成、隐私屏蔽等功能。
  - 要求：详细描述方案。如果违背整体规划，记录违背部分。完成后进行设计反思，记录反思结果。
- [x] Task 7: 编写 graph 模块详细设计文档及反思
  - 任务描述：作为最顶层的集成模块，参考整体规划及所有前置模块的反思结果，在 `docs/design/graph-module.md` 中设计 LangGraph 的 State 定义和图执行流。
  - 要求：详细描述方案。如果违背整体规划，记录违背部分。完成后进行最终设计反思。

# Task Dependencies
- Task 2 依赖于 Task 1。
- Task 3 依赖于 Task 1, Task 2。
- Task 4 依赖于 Task 1, Task 2。
- Task 5 依赖于 Task 1, Task 2, Task 4。
- Task 6 依赖于 Task 1, Task 2, Task 3, Task 4。
- Task 7 依赖于 Task 1, Task 2, Task 3, Task 4, Task 5, Task 6。
