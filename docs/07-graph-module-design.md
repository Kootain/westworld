# Graph 模块详细设计方案

## 1. 模块职责与定位

`graph` 模块是 LangGraph RPG-Agent 系统的心脏引擎。它的核心职责是基于 LangGraph 的 `StateGraph` 构建整个业务状态流转的 DAG（有向无环图）。
- 组装 `box`、`memory`、`agent` 模块的各个能力节点。
- 管理 `AgentState` 在节点间的传递与更新。
- 提供供外部调用的入口（通常是 `run_graph` 方法）。

## 2. 详细方案设计

### 2.1 状态定义 (`state.py`)
严格遵循总体规划中的 TypedDict 设计。
```python
from typing import TypedDict, List
from core.models import UserInput, AgentStatus, AgentAction, FinalOutput

class AgentState(TypedDict):
    user_input: UserInput
    current_status: AgentStatus
    sensory_memory: str
    retrieved_ltm: List[str]
    stm_context: List[str]
    agent_action: AgentAction
    final_output: FinalOutput
```

### 2.2 工作流节点定义 (`workflow.py`)

使用依赖注入的方式初始化各个服务（如 `IStatusGuard`），然后在图中作为节点。

#### 2.2.1 Box 前置节点
1. **状态守卫节点 (`box_filter_node`)**
   - 输入：`state['user_input']`、`state['current_status']`
   - 处理：调用 `StatusGuard.check_status`。如果拦截，则写入 `final_output`。
2. **感官合成节点 (`sensory_gen_node`)**
   - 输入：`state['user_input']`
   - 处理：调用 `SensoryGenerator` 生成主观感官记忆并更新到 `state['sensory_memory']`。

#### 2.2.2 认知环节点 (Agent Sub-Graph)
3. **联想与记忆提取节点 (`memory_recall_node`)**
   - 处理：通过 `state['sensory_memory']` 调用 LTM 检索，更新 `retrieved_ltm` 和 `stm_context`。
4. **思考决策节点 (`agent_plan_act_node`)**
   - 处理：调用大模型推理生成 `AgentAction`，更新 `agent_action`。

#### 2.2.3 Box 后置节点
5. **记忆固化评分与存储节点 (`memory_post_process_node`)**
   - 处理：将当前的感官刺激和 LLM 输出的 `agent_action`（包含重要性的内心活动和动作）通过特定算法打分后存入 STM。
6. **隐私屏蔽与过滤节点 (`box_output_node`)**
   - 处理：调用 `PrivacyFilter` 将 `agent_action` 转换为安全的 `final_output`。

### 2.3 边与条件路由 (Edges & Conditional Routing)

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("box_filter", box_filter_node)
workflow.add_node("sensory_gen", sensory_gen_node)
workflow.add_node("memory_recall", memory_recall_node)
workflow.add_node("agent_plan_act", agent_plan_act_node)
workflow.add_node("memory_post_process", memory_post_process_node)
workflow.add_node("box_output", box_output_node)

# 定义路由
def route_after_filter(state: AgentState):
    if state.get("final_output") is not None:
        # 已被拦截
        return END
    return "sensory_gen"

# 组装图
workflow.set_entry_point("box_filter")
workflow.add_conditional_edges("box_filter", route_after_filter)
workflow.add_edge("sensory_gen", "memory_recall")
workflow.add_edge("memory_recall", "agent_plan_act")
workflow.add_edge("agent_plan_act", "memory_post_process")
workflow.add_edge("memory_post_process", "box_output")
workflow.add_edge("box_output", END)

# 编译图
app = workflow.compile()
```

## 3. 与总体规划的偏差与修正

*偏差说明*：
总体规划的 Mermaid 图中，存在 `Auto_Reply[Box 直接代回]` 的分支节点。在 LangGraph 的实际实现中，当 `box_filter_node` 决定拦截时，可以直接为 State 的 `final_output` 赋值并路由到 `END`，而不需要一个专门的 `Auto_Reply` 节点。这种设计利用了 LangGraph 的条件路由特性，使得图结构更加简洁，且不违背原有的“状态拦截与阻断”的核心逻辑。
