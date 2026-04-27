from typing import Tuple
from src.core.enums import AgentStatus

class StatusGuard:
    def __init__(self):
        # 系统内部维护真实的 Agent 状态（或通过 Redis 读取）
        self.current_status: AgentStatus = AgentStatus.NORMAL
        
    def set_status(self, new_status: AgentStatus) -> None:
        self.current_status = new_status
        
    def check_interaction(self, player_input: str) -> Tuple[bool, str]:
        """
        检查当前状态是否允许交互。
        返回 (是否放行, 系统提示语)
        """
        if self.current_status == AgentStatus.SLEEPING:
            return False, "NPC 正在熟睡，没有听到你的声音。"
        elif self.current_status == AgentStatus.UNCONSCIOUS:
            return False, "NPC 目前处于昏迷状态，无法交互。"
            
        return True, ""
