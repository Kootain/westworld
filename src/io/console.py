import sys
import asyncio
from typing import Optional
from src.io.base import InputAdapter, OutputAdapter

class ConsoleInputAdapter(InputAdapter):
    async def receive(self) -> str:
        # 使用异步方式读取标准输入，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        print("\n[玩家]: ", end="", flush=True)
        return await loop.run_in_executor(None, sys.stdin.readline)

class ConsoleOutputAdapter(OutputAdapter):
    async def render(self, speech: Optional[str], action: Optional[str]) -> None:
        if action:
            print(f"\n*动作*: {action}")
        if speech:
            print(f"[NPC]: {speech}")

    async def render_system_message(self, message: str) -> None:
        print(f"\n[系统]: {message}")
