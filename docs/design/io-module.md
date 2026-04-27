# IO 模块详细设计文档

## 1. 模块职责
`io` 模块负责系统与外部环境的交互隔离。它的核心职责是：
1. 监听外部输入（如终端输入、Web请求、游戏客户端发包）。
2. 将系统的内部输出（角色的话语、动作）渲染给外部。

该模块**不允许**感知任何业务逻辑（如判断角色是否睡着，这是 `box` 的职责）。

## 2. 详细设计

### 2.1 抽象适配器设计 (`src/io/base.py`)
参考整体架构设计，定义抽象基类：

```python
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
        如果需要渲染环境事件，也可以通过重载或新增方法实现。
        """
        pass
```

### 2.2 控制台适配器实现 (`src/io/console.py`)
针对初期本地调试，实现 `ConsoleAdapter`：

```python
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
```

### 2.3 适配器工厂 (`src/io/factory.py`)
为了方便在主程序中注入：
```python
def get_input_adapter(adapter_type: str = "console") -> InputAdapter:
    if adapter_type == "console":
        return ConsoleInputAdapter()
    raise ValueError(f"Unknown adapter type: {adapter_type}")
```

## 3. 设计冲突与违背

在实现抽象时，发现了一个与初期规划**潜在冲突**的地方：
- **冲突描述**：初期 `docs/system-design.md` 中规定 `OutputAdapter.render(speech, action)` 仅接收 `speech` 和 `action`。但是 `box` 层不仅需要输出 Agent 的话语，还可能需要输出系统级提示（例如：“NPC 正在熟睡，没有听到你的声音”）。
- **违背处理**：在详细设计中，我们扩展了 `OutputAdapter` 的职责，增加了一个通用的 `render_system_message(msg: str)` 方法。
- **扩展后的 `OutputAdapter`**：
```python
class OutputAdapter(ABC):
    @abstractmethod
    async def render(self, speech: Optional[str], action: Optional[str]) -> None:
        pass
        
    @abstractmethod
    async def render_system_message(self, message: str) -> None:
        pass
```

## 4. 设计反思

**反思结论：**
1. **接口的灵活性**：单一的 `render` 方法不足以支撑丰富的交互形式。在后续 `box` 模块设计中，当 `box` 拦截了玩家请求时，必须调用 `io.render_system_message()` 而非将系统提示混入 `speech`，以保证表现层的语义正确。
2. **异步IO**：控制台的输入很容易导致整个线程阻塞。在 `ConsoleInputAdapter` 中，必须采用 `run_in_executor` 等异步技巧，这要求上层（`graph` / `box`）调用时必须全程 `await`。
3. **向下传递的约束**：`box` 模块在设计时，需要依赖扩展后的 `OutputAdapter` 接口，以便正确输出拦截提示。

## 5. 实现反思 (Implementation Reflection)
- **代码实现**: `src/io/base.py`, `src/io/console.py`, `src/io/factory.py` 均已实现并带有完整的类型注解与异步支持。
- **工厂方法扩展**: 除了原设计提到的 `get_input_adapter`，也实现了对应的 `get_output_adapter`，确保了对象的统一构造方式。
- **异步处理**: `ConsoleInputAdapter.receive` 中通过 `asyncio.get_event_loop().run_in_executor` 将阻塞的 `sys.stdin.readline` 放到独立线程中执行，避免了事件循环被卡死。
- **测试验证**: `tests/test_io.py` 通过 `monkeypatch` 和 `capsys` 对控制台输入输出进行了有效的单元测试覆盖，确保系统消息、普通输出等符合预期。
