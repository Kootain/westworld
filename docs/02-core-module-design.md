# Core 模块详细设计方案

## 1. 模块职责与定位

`core` 模块是整个 LangGraph RPG-Agent 系统的最底层基石。其主要职责包括：
1. **统一数据模型**：定义系统跨模块流转的核心 Pydantic 模型（如输入事件、智能体输出行为）。
2. **全局枚举与常量**：定义系统级的状态枚举（AgentStatus）与常量。
3. **全局配置管理**：解析和管理系统环境变量与配置文件（如 LLM API Key、数据库连接字符串）。
4. **异常类与工具库**：定义标准的系统自定义异常（Exceptions）和通用工具（如统一日志配置）。

该模块**绝对不能**反向依赖于 `box`、`memory`、`agent` 或 `graph` 模块，必须保持纯粹性。

## 2. 详细方案设计

### 2.1 全局配置管理 (`config.py`)
使用 `pydantic-settings` 统一管理环境配置。
- **职责**：加载 `.env` 文件，提供强类型的 `Settings` 对象。
- **包含字段**：`LLM_API_KEY`, `REDIS_URL`, `MILVUS_URI`, `LOG_LEVEL`, `MAX_STM_TOKENS` 等。

### 2.2 统一日志系统 (`logger.py`)
实现 `docs/system-design.md` 要求的“禁止裸 `print()`”和“执行流追踪”。
- **设计**：基于 `logging` 或 `loguru`，提供全局可用的 `get_logger(name)` 函数。
- **规范**：输出格式应包含时间戳、日志级别、模块名和具体信息。支持输出到控制台和文件。

### 2.3 核心数据模型 (`models.py`)
实现并扩展 `01-overall-planning.md` 中定义的模型。

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class AgentStatus(str, Enum):
    NORMAL = "NORMAL"
    SLEEPING = "SLEEPING"
    WORKING = "WORKING"
    UNCONSCIOUS = "UNCONSCIOUS"

class EventType(str, Enum):
    MESSAGE = "message"       # 玩家发送的对话/动作
    ENVIRONMENT = "environment" # 环境事件（如：天黑了）
    TICK = "tick"             # 后台时间流逝触发

class UserInput(BaseModel):
    user_id: str
    content: str
    event_type: EventType = EventType.MESSAGE

class AgentAction(BaseModel):
    speech: Optional[str] = Field(None, description="对外说出的话")
    action: Optional[str] = Field(None, description="身体动作或表情描写")
    sot: str = Field(..., description="真实的内心想法(Stream of Thought)")
    status_change: Optional[AgentStatus] = Field(None, description="申请改变自身状态")

class FinalOutput(BaseModel):
    speech: Optional[str] = None
    action: Optional[str] = None
    status: AgentStatus
```

### 2.4 全局异常基类 (`exceptions.py`)
定义系统的基础异常，方便上层捕获。
- `SystemBaseException`: 系统根异常
- `LLMGenerationException`: LLM 生成格式错误或超时
- `MemoryStorageException`: 数据库存储/读取失败

## 3. 与总体规划的偏差与修正

*当前设计与 `01-overall-planning.md` 完全吻合。对 `UserInput.event_type` 进行了强类型枚举（`EventType`）的扩充，使事件类型的分类更加严谨，这属于对整体设计的良性补充，不构成违背。*
