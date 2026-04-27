from pydantic import BaseModel, Field
from typing import Optional, List
from src.core.enums import AgentStatus

class AgentResponse(BaseModel):
    """
    智能体大模型单次认知决策的输出结构
    """
    Speech: Optional[str] = Field(default=None, description="对外说出的话")
    Action: Optional[str] = Field(default=None, description="身体动作或表情描写")
    SoT: str = Field(description="真实的内心想法（Stream of Thought）")
    Status_Change: Optional[AgentStatus] = Field(default=None, description="申请改变自身状态")

class SensoryData(BaseModel):
    """
    由 Box 模块合成的结构化感官数据
    """
    environment_events: List[str] = Field(default_factory=list, description="环境事件，如天黑了")
    user_inputs: List[str] = Field(default_factory=list, description="玩家输入")
    timestamp: float = Field(description="事件发生的时间戳")
