# LangGraph RPG-Agent System Spec

## Why
构建一个基于 LangGraph 的虚拟角色扮演系统（RPG-Agent），重点解决系统规则与智能体主观意识解耦的问题，并实现模拟人类遗忘与固化机制的三级存储架构。保证高扩展性、清晰的代码模块化以及支持多端接入的插件化 I/O，使系统具备极强的真实感与“活人感”。

## What Changes
- 设计并实现**系统容器 (Box)**，作为“物理定律”和“过滤器”，负责拦截、状态守卫、感官合成以及隐私（内心独白）屏蔽。
- 设计并实现**记忆模块 (Memory)**，包含极短期感官记忆 (Sensory)、带打分和逐出机制的短期记忆 (STM) 以及可异步固化的长期记忆 (LTM)。
- 设计并实现**智能体认知循环 (Agent Cognitive Loop)**，包含感知、联想、深度思考 (SoT) 和行为决策节点。
- 实现基于 LangGraph 的**全局工作流**。
- 实现**“活人感”外显系统 (Evidence of Life)**，包括后台时间流逝系统 (Tick) 和虚拟朋友圈 (Moments) 异步生成。
- 引入**插件化 I/O 设计**，抽象输入输出接口，支持 Console、Web API 等多种接入方式。
- 制定严格的 **Clean Code** 规范，确保各模块单一职责与高度抽象。

## Impact
- Affected specs: 这是一个全新项目，将奠定整体的系统架构和开发范式。
- Affected code: 项目根目录下的所有核心模块（预期包含 `/src/box`, `/src/memory`, `/src/agent`, `/src/io`, `/src/graph` 等）。

## ADDED Requirements

### Requirement: 插件化 I/O 系统
系统 SHALL 提供统一的输入输出抽象接口（如 `InputAdapter`, `OutputAdapter`），实现业务逻辑与具体展示层的解耦，方便未来接入不同的终端（如 CLI, HTTP API, WebSocket）。

### Requirement: 系统容器 (Box)
- 系统 SHALL 实现流量调度与状态守卫机制，在智能体处于“不可交互”状态（如疲劳、睡觉、昏迷）时，直接生成系统回复，阻断流量进入 LLM。
- 系统 SHALL 负责将原始输入和环境事件合成为感官记忆 (Sensory Memory)。
- 系统 SHALL 负责隐私屏蔽，接收智能体的全量输出（包含心理活动 SoT），过滤掉内心独白后，仅将对话和动作外显给玩家。

### Requirement: 三级记忆架构
系统 SHALL 实现分层存储策略：
1. **感官记忆 (Sensory Memory)**：作为当前 Graph 运行周期的极短期缓存。
2. **短期记忆 (STM)**：作为工作内存，带有基于时间与重要性的衰减评分公式 ($V = I \cdot e^{-\lambda(T_{now} - T_{created})}$)。当总 Token 超出阈值时，按 $V$ 值由低到高逐出。
3. **长期记忆 (LTM)**：作为核心人格与历史事实库，集成向量数据库与关系型数据库，并支持定期调用 LLM 对 STM 进行总结和异步固化。

### Requirement: 智能体认知循环
系统 SHALL 将智能体实现为一个 LangGraph Sub-Graph，依次执行：
1. 感知过滤 (Perceive)：决定注意力焦点。
2. 联想检索 (Recall)：从 LTM 中提取相关记忆注入上下文。
3. 深度思考 (SoT/Plan)：在内部进行逻辑推演。
4. 行为决策 (Act)：生成多维输出（Speech, Action, Status_Change）。

### Requirement: “活人感”外显系统
- 系统 SHALL 提供后台 Tick 机制以模拟时间流逝（例如：如果玩家长时间无操作，Box 自动注入环境事件如“天黑了”）。
- 系统 SHALL 支持异步触发器，在智能体状态发生重大变更时，异步提取 LTM 摘要，生成图像 Prompt 和文案，形成“虚拟朋友圈 (Moments)”。
