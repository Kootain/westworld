from langgraph.graph import StateGraph, END
from src.graph.state import AppState
from src.box.facade import BoxFacade
from src.agent.nodes import AgentNodes

class WorkflowBuilder:
    def __init__(self, box: BoxFacade, agent_nodes: AgentNodes):
        self.box = box
        self.agent = agent_nodes
        
    def build(self):
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
    async def _node_box_guard(self, state: AppState):
        is_safe, msg = self.box.check_safety(state["player_input"])
        if not is_safe:
            return {"system_reply": msg}
        
        # 如果安全，进行感官合成
        sensory_data = self.box.synthesize_sensory(
            events=state["environment_events"],
            player_input=state["player_input"]
        )
        return {"sensory_data": sensory_data, "system_reply": None}
        
    async def _node_auto_reply(self, state: AppState):
        if state.get("system_reply"):
            await self.box.format_system_reply(state["system_reply"])
        return {}
        
    async def _node_perceive(self, state: AppState):
        focus = await self.agent.perceive(state["sensory_data"])
        return {"attention_focus": focus}
        
    async def _node_recall(self, state: AppState):
        contexts = await self.agent.recall(state["sensory_data"])
        return {"stm_context": contexts["stm_context"], "ltm_context": contexts["ltm_context"]}
        
    async def _node_act(self, state: AppState):
        response = await self.agent.act(
            sensory_data=state["sensory_data"],
            stm_context=state.get("stm_context", ""),
            ltm_context=state.get("ltm_context", "")
        )
        return {"agent_response": response}
        
    async def _node_post_process(self, state: AppState):
        await self.agent.post_process(
            sensory_data=state["sensory_data"],
            agent_response=state["agent_response"]
        )
        return {}
        
    async def _node_box_output(self, state: AppState):
        if state.get("agent_response"):
            await self.box.format_output(state["agent_response"])
        return {}

    # --- 路由方法 ---
    def _route_after_guard(self, state: AppState) -> str:
        if state.get("system_reply"):
            return "intercept"
        return "continue"
        
    def _route_after_perceive(self, state: AppState) -> str:
        if state.get("attention_focus"):
            return "focus"
        return "ignore"
