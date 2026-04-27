# Agent 模块详细设计方案

## 1. 模块职责与定位

`agent` 模块是系统的认知引擎层。它的核心任务是承载 LangGraph 中定义好的“思考节点”的具体业务逻辑与 LLM 交互。
它**不负责**工作流的调度编排（那是 `graph` 模块的职责），而是为工作流提供纯净的节点函数（Node Functions）。

## 2. 详细方案设计

基于 `01-overall-planning.md` 和 `docs/system-design.md`，认知循环被拆解为以下核心阶段，每个阶段对应一个模块文件及相应的 Prompt 管理。

### 2.1 目录结构划分
```text
agent/
  ├── prompts/         # 集中管理所有系统提示词模板
  ├── nodes/
  │   ├── perceive.py  # 节点：感知与焦点过滤
  │   ├── recall.py    # 节点：联想与检索 LTM
  │   ├── plan.py      # 节点：深度思考与决策
  │   └── action.py    # 节点：结构化动作输出
  └── llm_client.py    # 封装对 OpenAI/Anthropic 的统一 API 调用
```

### 2.2 核心节点逻辑设计

所有的节点函数签名应当符合 LangGraph 状态机节点规范：接受当前 `AgentState`，返回需要更新的 `AgentState` 字典。

#### 2.2.1 感知过滤 (`perceive.py`)
- **逻辑**：接收 `state['sensory_memory']` 和 `state['current_status']`。
- **动作**：调用一个轻量级 LLM，判断当前感官刺激是否值得引起智能体的注意。
- **输出**：生成一个提取后的“注意力焦点 (Attention Focus)”供后续使用。

#### 2.2.2 联想检索 (`recall.py`)
- **逻辑**：使用上一步的“注意力焦点”作为 Query，调用 `memory.ltm.search(query)`。
- **输出**：将检索到的背景设定和历史记忆更新到 `state['retrieved_ltm']` 中。同时调用 `memory.stm.get_recent_memories()` 加载到 `state['stm_context']`。

#### 2.2.3 深度思考与行为决策 (`plan_and_act.py`)
为了减少 LLM 调用的延迟和成本，将 SoT(思维链)和 Act(行为输出) 合并为一次 LLM 调用（通过 System Prompt 强制要求先输出思考过程，再输出结果 JSON）。
- **输入组装**：
  - System Prompt：NPC 的人设、性格特征、当前的 Box 物理状态限制。
  - Context：`state['retrieved_ltm']` + `state['stm_context']` + `state['sensory_memory']`。
- **LLM 调用**：要求 LLM 返回严格符合 `core.models.AgentAction` 的 JSON。可以使用 LangChain 的 `with_structured_output` 或直接使用 Pydantic Parser。
- **输出**：将生成的 `AgentAction` 写入 `state['agent_action']`。

## 3. 与总体规划的偏差与修正

*偏差说明*：在总体规划的 `3.3 LangGraph 工作流设计` 中，`SoT_Planning` 和 `Action_Gen` 被描绘为可能分开的步骤。但在本模块的详细设计中，出于**性能和成本考量**，建议将它们**合并为一个节点**（`plan_and_act`），让 LLM 在同一次流式生成中，先写 `sot`（作为思维链的推理过程），接着输出 `speech` 和 `action`。这并不违背“思维必须发生并被记录”的核心设计初衷，反而提高了推演的一致性。该修正将在 `graph` 模块的最终编排中体现。
