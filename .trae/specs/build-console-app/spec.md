# Build Console App Spec

## Why
目前所有底层和核心业务模块（`core`, `io`, `memory`, `agent`, `box`, `graph`）均已实现并经过测试。我们需要一个实际的可执行入口点来将它们组装起来，测试端到端的工作流（感知、思考、行为以及控制台 I/O 的交互），以验证整个系统在终端下的真实表现。

## What Changes
- 在 `cmd/console_test/` 目录下创建控制台应用的入口文件 `main.py`。
- 在 `main.py` 中初始化 `io` 模块的 `ConsoleInputAdapter` 和 `ConsoleOutputAdapter`。
- 初始化 `core` 模块的时间管理器和日志。
- 初始化 `memory` 的 `MemoryFacade`。
- 初始化 `agent` 的 `AgentNodes`（由于是测试，这里可以注入一个模拟或真实的 LLMClient）。
- 初始化 `box` 的 `BoxFacade`。
- 将上述依赖注入到 `graph` 模块的 `WorkflowBuilder` 中，编译生成 LangGraph 工作流实例。
- 编写一个 `while True` 的异步交互循环，不断读取控制台输入，将输入封装成初始状态并驱动 LangGraph 运行，从而实现持续的终端对话。

## Impact
- Affected specs: 提供了系统首个交互式的可运行入口点，用于端到端验证。
- Affected code: 新增了 `cmd/console_test/main.py` 目录及文件，不修改原有核心模块逻辑。

## ADDED Requirements
### Requirement: 基于 Console 的交互对话循环
系统应提供一个命令行交互界面，能够接收玩家输入并通过完整的架构管线处理，最终将智能体的回复（动作、语言或系统拦截消息）输出回终端。

#### Scenario: Success case
- **WHEN** 玩家在终端运行 `python -m cmd.console_test.main` 并输入对话时
- **THEN** 终端能够即时显示玩家的输入，调用内部的 graph 流程，随后显示系统拦截消息或 NPC 返回的动作和语言。
