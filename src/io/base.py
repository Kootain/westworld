from abc import ABC, abstractmethod
from typing import Optional

class InputAdapter(ABC):
    """
    负责从外部源接收玩家或系统输入。
    """
    @abstractmethod
    async def receive(self) -> str:
        """
        阻塞等待并返回一条外部输入字符串。
        """
        pass

class OutputAdapter(ABC):
    """
    负责将 Agent 的输出渲染给外部源。
    """
    @abstractmethod
    async def render(self, speech: Optional[str], action: Optional[str]) -> None:
        """
        接收语音和动作并渲染。
        """
        pass

    @abstractmethod
    async def render_system_message(self, message: str) -> None:
        """
        输出系统级提示
        """
        pass
