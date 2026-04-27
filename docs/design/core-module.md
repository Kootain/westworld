# Core 模块详细设计文档

## 1. 模块职责
`core` 模块是系统的基础基石。主要包含：
1. 全局配置加载与管理（Config）。
2. 全局通用的基础数据结构和枚举（Pydantic Models & Enums）。
3. 跨模块的基础工具类（如时间管理、日志配置、Token 计算等）。

该模块不包含任何具体的业务流转逻辑，**零外部业务依赖**，被系统中所有其他模块依赖。

## 2. 详细设计

### 2.1 全局枚举类 (`src/core/enums.py`)
定义系统中具有固定状态的枚举：

```python
from enum import Enum

class AgentStatus(str, Enum):
    NORMAL = "NORMAL"
    SLEEPING = "SLEEPING"
    WORKING = "WORKING"
    UNCONSCIOUS = "UNCONSCIOUS"
    
class MemoryType(str, Enum):
    SENSORY = "SENSORY"
    STM = "STM"
    LTM = "LTM"
```

### 2.2 全局数据模型 (`src/core/models.py`)
定义跨模块交互的数据结构，统一使用 `pydantic` 进行校验：

```python
from pydantic import BaseModel, Field
from typing import Optional
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
    environment_events: list[str] = Field(default_factory=list, description="环境事件，如天黑了")
    user_inputs: list[str] = Field(default_factory=list, description="玩家输入")
    timestamp: float = Field(description="事件发生的时间戳")
```

### 2.3 全局配置管理 (`src/core/config.py`)
基于 `pydantic-settings` 的配置加载：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Settings
    LLM_API_KEY: str
    LLM_MODEL_NAME: str = "gpt-4-turbo"
    
    # Memory Settings
    STM_TOKEN_LIMIT: int = 4000
    DECAY_RATE: float = 0.01  # 记忆衰减系数 lambda
    
    # Vector DB Settings
    MILVUS_URI: str = "./milvus.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2.4 基础工具类 (`src/core/utils.py`)
包含时间流逝模拟、日志初始化等：
- `setup_logging()`: 封装 `loguru` 或标准 `logging`，提供统一格式。
- `TimeManager`: 维护系统内的虚拟时间戳。

## 3. 设计冲突与违背

在目前设计阶段，`core` 模块的设计与整体架构规划**无冲突**。
- `AgentResponse` 和 `SensoryData` 遵循了架构中对 Pydantic 的要求。

## 4. 设计反思

**反思结论：**
1. **模型拆分粒度**：起初想把所有 Model 都放在 `core` 中，但反思发现，只有“跨模块共享”的 Model（如 `AgentResponse`, `AgentStatus`）才应放入 `core`。如果某个 Model 仅由 `memory` 内部使用（如 `MemoryNode`），应放在 `memory` 模块内部，以避免 `core` 变得臃肿。
2. **向下传递的约束**：后续 `io` 和 `memory` 模块在定义内部数据结构时，尽量复用 `core/models.py`，但不要强行将私有模型塞入 `core`。
