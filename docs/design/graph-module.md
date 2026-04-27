# Graph 模块详细设计文档

## 1. 模块职责
`graph` 模块是系统的神经中枢。它基于 LangGraph 框架，将 `io`, `box`, `memory`, `agent` 组装成一个完整的有向图（Directed Graph）。
主要职责包括：
1. **全局 State 定义**：定义在图中流转的数据结构 `TypedDict`。
2. **工作流编排**：注册各个 Node，并根据条件（Conditional Edges）编排执行顺序。
3. **图的编译与运行**：对外提供 `compile()` 和 `run()` 方法。

## 2. 详细设计

### 2.1 全局 State 定义 (`src/graph/state.py`)
基于 `agent` 和 `box` 模块的反思，为了解耦，`State` 应当仅包含核心上下文数据，不要把各模块私有的实例放进去：

```python
from typing import TypedDict, List, Optional
from src.core.models import SensoryData, AgentResponse

class AppState(TypedDict):
    """
    在 LangGraph 节点之间流转的数据字典
    """
    # 来自外部的原始输入
    player_input: str
    environment_events: List[str]
    
    # Box 处理后的数据
    sensory_data: Optional[SensoryData]
    system_reply: Optional[str]  # 拦截时的系统回复
    
    # Agent 处理过程的数据
    stm_context: str
    ltm_context: str
    attention_focus: bool  # perceive 节点决定是否关注
    
    # Agent 的最终决策
    agent_response: Optional[AgentResponse]
```

### 2.2 工作流编排 (`src/graph/builder.py`)
根据之前各个模块的反思，重新编排执行流：

```python
from langgraph.graph import StateGraph, END
from src.graph.state import AppState

class WorkflowBuilder:
    def __init__(self, box, agent_nodes, io_adapter):
        self.box = box
        self.agent = agent_nodes
        self.io = io_adapter
        
    def build(self) -> StateGraph:
        workflow = StateGraph(AppState)
        
        # --- 注册节点 (Nodes) ---
        # Box 拦截与感官合成
        workflow.add_node("box_guard", self._node_box_guard)
        workflow.add_node("auto_reply", self._node_auto_reply)
        
        # Agent 认知链
        workflow.add_node("perceive", self._node_perceive)
        workflow.add_node("recall", self._node_recall)
        workflow.add_node("act", self._node_act)
        workflow.add_node("post_process", self._node_post_process) # 来自 agent 模块反思
        
        # 输出渲染
        workflow.add_node("box_output", self._node_box_output)
        
        # --- 注册边 (Edges) ---
        workflow.set_entry_point("box_guard")
        
        # Box 守卫的条件分支
        workflow.add_conditional_edges(
            "box_guard",
            self._route_after_guard,
            {
                "continue": "perceive",
                "intercept": "auto_reply"
            }
        )
        
        # 拦截分支：自动回复 -> 结束
        workflow.add_edge("auto_reply", END)
        
        # 正常认知分支
        workflow.add_conditional_edges(
            "perceive",
            self._route_after_perceive,
            {
                "focus": "recall",
                "ignore": END
            }
        )
        
        workflow.add_edge("recall", "act")
        workflow.add_edge("act", "post_process")
        workflow.add_edge("post_process", "box_output")
        workflow.add_edge("box_output", END)
        
        return workflow.compile()
        
    # --- 节点封装方法 ---
    # 这里通过解包 State 调用具体模块的方法，实现 State 与业务模块的解耦（回应 agent 模块的反思）
    def _node_act(self, state: AppState):
        response = self.agent.act(
            sensory_data=state["sensory_data"],
            stm_context=state["stm_context"],
            ltm_context=state["ltm_context"]
        )
        return {"agent_response": response}
```

## 3. 设计冲突与违背

在整合所有模块的反思后，我们发现：
- **冲突描述**：初期架构图中并没有 `post_process` 节点，且 `Box_Filter` 作为一个节点处理所有的分流。
- **违背处理**：我们在 `WorkflowBuilder` 中正式确立了 `post_process` 作为图中标准节点的存在，并把 `Box_Filter` 拆分成了 `box_guard`, `auto_reply`, 和 `box_output` 三个独立的逻辑节点。这样不仅符合 LangGraph 的设计模式，也解决了 `agent` 模块的 SoT 打分存储问题。

## 4. 设计反思（最终总结）

**反思结论：**
1. **解耦的成功**：通过在 `WorkflowBuilder` 中进行“解包调用”（如 `self.agent.act(sensory, stm, ltm)`），我们成功地让 `agent` 和 `box` 模块完全摆脱了对 LangGraph `State` 的强依赖。它们变成了纯粹的业务类，只有 `graph` 模块知道图是怎么流转的。
2. **IoC（控制反转）的落地**：整个系统的依赖注入（DI）应该放在 `main.py` 中。`main.py` 实例化 `core` 配置、`io` 适配器、`memory` 门面、`box` 容器和 `agent` 节点，最后把它们喂给 `WorkflowBuilder`。
3. **架构闭环**：至此，从 `core` 到 `graph` 的六个模块已经完成逻辑闭环，每个模块的边界清晰，接口明确，完全符合初期 `docs/system-design.md` 的宏伟目标。
