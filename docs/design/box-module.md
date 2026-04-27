# Box 模块详细设计文档

## 1. 模块职责
`box` 模块是系统的“物理法则”与“过滤器”，作为最顶层的拦截机制，负责：
1. **状态守卫 (Status Guard)**：拦截不可交互的状态（如睡觉）。
2. **感官合成 (Sensory Generator)**：将玩家输入与环境事件转化为系统级感官数据。
3. **隐私屏蔽 (Privacy Filter)**：在最后输出给玩家前，剥离内心独白（SoT），只呈现行为与话语。
4. **后台 Tick 机制支持**：通过注入虚拟时间事件，推动 Agent 产生自发行为。

## 2. 详细设计

### 2.1 状态守卫实现 (`src/box/guard.py`)
在处理任何玩家输入前，首先判断 Agent 状态：

```python
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
```

### 2.2 感官合成器 (`src/box/sensory.py`)
结合玩家输入和时间流逝（后台 Tick）：

```python
from src.core.models import SensoryData
from src.core.utils import TimeManager

class SensoryGenerator:
    def __init__(self, time_manager: TimeManager):
        self.time_manager = time_manager
        
    def generate(self, player_inputs: list[str], environment_events: list[str]) -> SensoryData:
        return SensoryData(
            environment_events=environment_events,
            user_inputs=player_inputs,
            timestamp=self.time_manager.current_time()
        )
```

### 2.3 隐私过滤器与渲染门面 (`src/box/filter.py`)
`box` 作为输出把关者，拦截 AgentResponse，通过 `io` 渲染给玩家：

```python
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
```

## 3. 设计冲突与违背

在详细设计中，我们发现了一个与 `docs/system-design.md` 的潜在冲突：
- **冲突描述**：初期架构图中，`Box 状态守卫` 作为 LangGraph 图的第一个 Node `Box_Filter`。但是，如果 `Box` 只是 LangGraph 中的一个节点，它本身在图启动后才被调用。如果 `Box` 决定拦截请求，它必须提前终止图的运行。
- **违背处理**：在详细设计中，我们决定将 `Box` 的拦截逻辑（`StatusGuard` 和 `SensoryGenerator`）前置在 LangGraph 图**外部**（或作为一个路由前置条件 `conditional_edge`），而把 `PrivacyFilter` 放在图的最后一步。
- **结论**：`box` 的组件实际上被拆分成了两部分：图执行前置逻辑与图执行后置逻辑。

## 4. 设计反思

**反思结论：**
1. **控制流反转**：`box` 模块的拦截如果发生在 `graph` 内部，需要利用 LangGraph 的 `END` 节点直接退出，并更新状态。这使得 `box` 的拦截逻辑高度依赖 LangGraph 框架。
2. **向后传递的约束**：在接下来的 `graph` 模块设计中，我们必须决定如何实现这个“直接阻断”。最佳实践是：
   - 第一步节点：`box_guard_node`。
   - 然后有一个 `conditional_edge`：如果状态不可交互，则跳转到 `auto_reply_node`，然后直接 `END`。
   - 否则跳转到 `agent` 的 `perceive` 节点。
   - 最终无论是走完 Agent 流程，还是被 `auto_reply_node` 代回，最终输出前都走 `box_filter_node` 调用 `io`。
3. **IO 的注入**：`io` 的实例应该在 `main.py` 中初始化，然后注入到 `box` 中，而 `graph` 模块通过调用 `box` 的方法来实现输出，从而彻底解耦 `agent` 与 `io`。
