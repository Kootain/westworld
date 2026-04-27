# Tasks

基于完善的需求与架构设计文档，我们将整体工程化实施划分为以下几个阶段的独立任务。当前为**需求确认阶段**，后续为**代码实施阶段**。

## Phase 1: 需求分析与架构设计 (Current)
- [x] Task 1.1: 撰写包含功能需求、架构需求、代码规范的完整 PRD 与设计文档 (`spec.md`)。
- [x] Task 1.2: 对齐 LangGraph 工作流、三级记忆体系、以及 I/O 插件化方案。

## Phase 2: 基础设施与 I/O 抽象开发
- [ ] Task 2.1: 搭建符合规范的目录结构 (`src/io`, `src/box`, `src/memory`, `src/agent`, `src/graph`, `src/core`)。
- [ ] Task 2.2: 定义基础数据模型 (使用 Pydantic 定义 `AgentState`, `SensoryData`, `ActionOutput` 等)。
- [ ] Task 2.3: 实现 `InputAdapter` 和 `OutputAdapter` 抽象基类。
- [ ] Task 2.4: 实现 `ConsoleAdapter` 以支持后续的本地联调。
- [ ] Task 2.5: 配置全局 `Logging` 系统。

## Phase 3: 核心记忆系统 (Memory System) 开发
- [ ] Task 3.1: 开发极短期感官记忆 (`SensoryMemory`) 模块。
- [ ] Task 3.2: 开发短期记忆 (`STM`) 引擎，实现时间与重要性衰减算法 ($V = I \cdot e^{-\lambda(T_{now} - T_{created})}$) 及容量逐出策略。
- [ ] Task 3.3: 定义长期记忆 (`LTM`) 接口，并使用本地 JSON/SQLite 提供 Mock 实现（预留向量检索扩展）。
- [ ] Task 3.4: 开发记忆固化 (`Consolidation`) 逻辑，通过 LLM 总结 STM 存入 LTM。

## Phase 4: 系统容器 (Box Orchestrator) 开发
- [ ] Task 4.1: 实现 `Agent_Status` 枚举与状态管理类。
- [ ] Task 4.2: 开发 `StatusGuard`（状态守卫）节点，实现对“不可交互”状态的请求拦截。
- [ ] Task 4.3: 开发 `SensoryGenerator`，合并外部输入与环境数据。
- [ ] Task 4.4: 开发 `PrivacyFilter`，负责从大模型输出中剥离 `SoT` 内心独白字段。

## Phase 5: 智能体认知链 (Agent Sub-Graph) 开发
- [ ] Task 5.1: 实现 `Perceive` 节点逻辑及 Prompt 模板。
- [ ] Task 5.2: 实现 `Recall` 节点逻辑，对接 LTM 进行上下文 RAG。
- [ ] Task 5.3: 实现 `SoT/Planning` (深度思考) 节点逻辑。
- [ ] Task 5.4: 实现 `Act` 节点逻辑，使用 Pydantic 约束 LLM 强制输出 JSON (Speech, Action, SoT, Status_Change)。

## Phase 6: 全局 LangGraph 组装与外显系统
- [ ] Task 6.1: 在 `src/graph` 中定义 State，组装 Box 节点与 Agent Sub-Graph，并配置条件边 (Conditional Edges)。
- [ ] Task 6.2: 编写测试脚本，跑通端到端的 Console 交互流。
- [ ] Task 6.3: 开发后台 Tick 机制（时间流逝与自动环境事件注入）。
- [ ] Task 6.4: 开发“虚拟朋友圈” (Moments) 异步生成流。
