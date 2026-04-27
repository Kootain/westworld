# Tasks
- [x] Task 1: 搭建应用目录结构与基础入口框架
  - 任务描述：创建 `cmd/console_test` 目录，并在其中创建 `main.py` 文件，设置基本的 `asyncio` 运行框架。
- [x] Task 2: 依赖实例化与注入
  - 任务描述：在 `main.py` 中初始化所有必须的组件（`TimeManager`, `ConsoleInputAdapter`, `ConsoleOutputAdapter`, `MemoryFacade`, `BoxFacade`, 模拟或基础的 `LLMClient`, `AgentNodes`）。
- [x] Task 3: 图编排与编译
  - 任务描述：实例化 `WorkflowBuilder`，注入第2步中的组件，调用 `build()` 编译生成 `workflow`。
- [x] Task 4: 实现交互循环
  - 任务描述：编写一个 `while True` 的异步循环，读取用户输入（通过 `ConsoleInputAdapter`），构造包含 `player_input` 的初始 State 字典，调用 `workflow.ainvoke` 执行，以实现持续对话体验。处理退出命令（如输入 "exit" 或 "quit" 时退出循环）。

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 2
- Task 4 依赖于 Task 3
