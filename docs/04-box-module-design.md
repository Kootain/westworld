# Box 模块详细设计方案

## 1. 模块职责与定位

`box` 模块是系统的物理法则层，代表客观世界的规则，优先级高于智能体的自由意志。
核心职责：
1. **状态守卫 (Status Guard)**：在请求到达 Agent 之前，检查智能体状态是否允许交互，负责流量拦截。
2. **感官合成 (Sensory Generator)**：将玩家输入、系统 Tick 或环境事件合成为统一的感官视角描述。
3. **隐私屏蔽 (Privacy Filter)**：在最终输出前，强制过滤掉 Agent 的内心独白（SoT），只输出外显内容。

## 2. 详细方案设计

### 2.1 状态守卫 (`status_guard.py`)
- **实现 `IStatusGuard` 接口**。
- **逻辑**：
  - 如果 `current_status == AgentStatus.SLEEPING` 且输入类型是普通对话，返回拦截标志，并生成系统代回（如：“NPC正在熟睡，没有回应”）。
  - 如果输入事件是非常强烈的环境事件（如：“发生地震了”），可能允许突破状态限制（将状态强制唤醒），允许请求进入 Agent。

```python
from core.models import AgentStatus, UserInput, FinalOutput, EventType
from typing import Tuple, Optional

class StatusGuard:
    def check_status(self, current_status: AgentStatus, user_input: UserInput) -> Tuple[bool, Optional[FinalOutput]]:
        if current_status == AgentStatus.SLEEPING:
            if user_input.event_type == EventType.MESSAGE:
                return False, FinalOutput(
                    speech=None,
                    action="继续沉睡，没有反应",
                    status=current_status
                )
            # 若是强烈物理环境事件可唤醒，放行
        elif current_status == AgentStatus.UNCONSCIOUS:
            return False, FinalOutput(action="处于昏迷状态", status=current_status)
            
        # 默认放行
        return True, None
```

### 2.2 感官合成器 (`sensory_gen.py`)
- **实现 `ISensoryGenerator` 接口**。
- **逻辑**：将客观的输入转换为 NPC 第一人称的主观感官描述。

```python
class SensoryGenerator:
    def generate_sensory_data(self, user_input: UserInput, environment_context: dict) -> str:
        if user_input.event_type == EventType.MESSAGE:
            return f"你听到 {user_input.user_id} 对你说/做了: {user_input.content}"
        elif user_input.event_type == EventType.ENVIRONMENT:
            return f"你察觉到环境发生变化: {user_input.content}"
        elif user_input.event_type == EventType.TICK:
            time_passed = user_input.content
            return f"时间流逝了 {time_passed}。目前环境：{environment_context.get('weather', '未知')}。"
        return user_input.content
```

### 2.3 隐私过滤器 (`privacy_filter.py`)
- **实现 `IPrivacyFilter` 接口**。
- **逻辑**：将 `AgentAction` 转换为 `FinalOutput`，丢弃 `sot` 字段，处理状态变更请求。

```python
from core.models import AgentAction, AgentStatus, FinalOutput

class PrivacyFilter:
    def filter_output(self, agent_action: AgentAction, current_status: AgentStatus) -> FinalOutput:
        # 判断状态变更是否被允许 (Box拥有最终决定权)
        new_status = current_status
        if agent_action.status_change and agent_action.status_change != current_status:
            # 此处可添加Box级校验规则，暂且允许自由切换
            new_status = agent_action.status_change
            
        return FinalOutput(
            speech=agent_action.speech,
            action=agent_action.action,
            status=new_status
        )
```

## 3. 与总体规划的偏差与修正

*偏差说明*：总体规划中提到 Box 可能需要维护状态，但在具体设计中，`current_status` 被提取为 `AgentState` 的一部分流转。因此 `StatusGuard` 和 `PrivacyFilter` 被设计为无状态的纯函数式服务，依赖图节点传入的当前状态进行判断。此设计更加符合 LangGraph 的函数式节点范式，提升了可测试性。
