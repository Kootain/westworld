from src.core.models import AgentResponse
from src.io.base import OutputAdapter

class PrivacyFilter:
    def __init__(self, output_adapter: OutputAdapter):
        self.io = output_adapter
        
    async def render_to_player(self, response: AgentResponse) -> None:
        """
        核心过滤器：拦截了 SoT，只透传 Speech 和 Action
        """
        # 注意：这里直接忽略了 response.SoT 字段，实现了隐私屏蔽
        await self.io.render(speech=response.Speech, action=response.Action)
        
    async def render_system_message(self, message: str) -> None:
        """
        利用 io 模块反思中新增的接口，输出系统提示
        """
        await self.io.render_system_message(message)
