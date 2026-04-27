# I/O 模块详细设计方案

## 1. 模块职责与定位

`io` 模块负责处理系统的输入和输出层，实现与物理介质（终端、Web端、游戏客户端）的解耦。
其核心职责是：
1. 提供 `InputAdapter` 和 `OutputAdapter` 抽象基类。
2. 实现具体的适配器（初期重点实现 `ConsoleAdapter`）。
3. 确保任何与外部系统的交互都不侵入 `box` 或 `agent` 核心逻辑。

## 2. 详细方案设计

### 2.1 适配器抽象定义 (`base.py`)
定义输入输出的契约，完全遵循 `01-overall-planning.md`。

```python
from abc import ABC, abstractmethod
from core.models import UserInput, FinalOutput

class InputAdapter(ABC):
    @abstractmethod
    async def receive(self) -> UserInput:
        """阻塞或异步等待外部输入，转化为 UserInput"""
        pass

class OutputAdapter(ABC):
    @abstractmethod
    async def render(self, output: FinalOutput) -> None:
        """接收系统的 FinalOutput 并渲染到外部介质"""
        pass
```

### 2.2 控制台适配器实现 (`console.py`)
用于本地开发与调试。

```python
import asyncio
from .base import InputAdapter, OutputAdapter
from core.models import UserInput, FinalOutput, EventType

class ConsoleInputAdapter(InputAdapter):
    def __init__(self, user_id: str = "local_player"):
        self.user_id = user_id

    async def receive(self) -> UserInput:
        # 使用 ainput 模拟异步等待终端输入
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, input, f"\n[{self.user_id}] > ")
        
        # 简单模拟：如果输入以 /env 开头，则视为环境事件
        if content.startswith("/env "):
            return UserInput(user_id=self.user_id, content=content[5:], event_type=EventType.ENVIRONMENT)
            
        return UserInput(user_id=self.user_id, content=content, event_type=EventType.MESSAGE)

class ConsoleOutputAdapter(OutputAdapter):
    async def render(self, output: FinalOutput) -> None:
        print("\n=== [系统输出] ===")
        print(f"当前状态: {output.status}")
        if output.action:
            print(f"动作: *{output.action}*")
        if output.speech:
            print(f"对话: 「{output.speech}」")
        print("==================\n")
```

### 2.3 FastAPI / WebSocket 适配器 (扩展预留)
在架构上保证可以轻易新增 `websocket.py` 或 `api.py`，只需继承 `InputAdapter` 和 `OutputAdapter`，在图启动时将具体实例注入到工作流即可。

## 3. 与总体规划的偏差与修正

*当前设计与总体规划完全一致，无偏差。抽象类依赖了 `core` 模块的数据结构，保证了边界的数据统一性。*
