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
