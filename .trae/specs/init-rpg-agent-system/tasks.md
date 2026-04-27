# Tasks

- [ ] Task 1: 项目初始化与 I/O 插件化抽象
  - [ ] SubTask 1.1: 初始化项目结构（遵循 Clean Code，划分 `box`, `memory`, `agent`, `io`, `graph` 目录）。
  - [ ] SubTask 1.2: 定义并实现 `InputAdapter` 和 `OutputAdapter` 抽象接口。
  - [ ] SubTask 1.3: 实现基于 Console 的本地 I/O 插件用于调试。

- [ ] Task 2: 实现记忆模块 (Memory Architecture)
  - [ ] SubTask 2.1: 定义极短期感官记忆 (Sensory Memory) 数据结构 (`TypedDict` 或 `JSON`)。
  - [ ] SubTask 2.2: 实现短期记忆 (STM) 模块，包含重要性打分、时间衰减公式及容量阈值逐出逻辑。
  - [ ] SubTask 2.3: 实现长期记忆 (LTM) 接口抽象，集成基础的向量/关系存储。
  - [ ] SubTask 2.4: 实现 STM 到 LTM 的定期异步固化 (Memory Consolidation) 逻辑。

- [ ] Task 3: 实现系统容器 (Box Orchestrator)
  - [ ] SubTask 3.1: 定义角色状态枚举与管理机制 (`Agent_Status`)。
  - [ ] SubTask 3.2: 实现状态守卫逻辑（不可交互状态的拦截与系统代回）。
  - [ ] SubTask 3.3: 实现感官合成器（合并玩家 Input 与 Environment Events）。
  - [ ] SubTask 3.4: 实现隐私屏蔽过滤器（剥离内心独白 SoT，保留对外可见的 Speech 和 Action）。

- [ ] Task 4: 实现智能体认知链 (Agent Brain Sub-Graph)
  - [ ] SubTask 4.1: 实现感知过滤节点 (Perceive)。
  - [ ] SubTask 4.2: 实现联想检索节点 (Recall)，基于焦点查询 LTM。
  - [ ] SubTask 4.3: 实现深度思考节点 (SoT/Planning)。
  - [ ] SubTask 4.4: 实现多维行为决策节点 (Action/Speech/Status_Change Generation)。
  - [ ] SubTask 4.5: 使用 LangGraph 将上述节点组装为 Sub-Graph。

- [ ] Task 5: 构建全局 LangGraph 工作流
  - [ ] SubTask 5.1: 组装全局 Graph，串联 Box 过滤器、智能体 Sub-Graph 及后处理节点。
  - [ ] SubTask 5.2: 整合 I/O 插件，实现端到端的整体运行闭环。

- [ ] Task 6: 实现“活人感”系统 (Evidence of Life)
  - [ ] SubTask 6.1: 实现后台 Tick 机制与环境事件自动注入逻辑。
  - [ ] SubTask 6.2: 实现虚拟朋友圈 (Moments) 异步生成触发器及多模态 Prompt 生成逻辑。
