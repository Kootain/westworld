# 整体模块职责规划与接口设计 (Overall Planning & Interface Design)

## 1. 总体架构规划

本系统 (LangGraph RPG-Agent) 的整体架构根据功能和业务隔离分为六大核心模块。各模块的职责规划如下：

### 1.1 `core` (核心基础模块)
- **职责**：提供系统级别的基础配置、全局共享的枚举定义（如智能体状态）、错误基类、以及跨模块使用的数据模型（Pydantic Models）。
- **定位**：系统最底层的依赖，不依赖于系统中的任何其他业务模块。

### 1.2 `io` (输入输出适配模块)
- **职责**：负责与外部环境的交互。抽象出系统的输入输出接口，实现业务逻辑与物理输入输出（控制台、WebSocket、FastAPI等）的完全解耦。
- **定位**：边界层。将外部的玩家指令、系统事件转换为系统内部统一的数据结构；将系统的最终响应渲染给外部。

### 1.3 `box` (系统容器与物理法则模块)
- **职责**：充当系统的“过滤器”与“上帝之手”。负责状态拦截（Status Guard）、感官合成（Sensory Generator）以及输出隐私屏蔽（Privacy Filter）。
- **定位**：系统层。在玩家输入进入大模型前进行干预，在大模型输出展示给玩家前进行脱敏。

### 1.4 `memory` (记忆架构模块)
- **职责**：管理智能体的三级记忆结构（感官记忆、短期记忆 STM、长期记忆 LTM）。处理记忆的衰减遗忘算法、向量存储和定期的异步固化（Consolidation）。
- **定位**：持久化与数据服务层。对外提供抽象的记忆存取 API。

### 1.5 `agent` (认知处理模块)
- **职责**：智能体的“大脑”。封装感知过滤（Perceive）、联想检索（Recall）、深度思考（SoT/Planning）和行为决策（Act）等核心认知节点的逻辑与 Prompt 模板。
- **定位**：认知层。通过调用大语言模型（LLM）实现真正的思考与决策。

### 1.6 `graph` (工作流调度模块)
- **职责**：基于 LangGraph 定义全局状态（State TypedDict），将 `box`、`memory` 和 `agent` 的各个节点组装成有向无环图（DAG），驱动整个业务数据流转。
- **定位**：调度与编排层。

---

## 2. 核心接口与数据模型设计 (Interface-First Design)

遵循契约式编程理念，以下定义系统各层交互的核心接口和数据结构。

### 2.1 核心数据结构 (Data Models in `core`)

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List

class AgentStatus(str, Enum):
    NORMAL = "NORMAL"
    SLEEPING = "SLEEPING"
    WORKING = "WORKING"
    UNCONSCIOUS = "UNCONSCIOUS"

class UserInput(BaseModel):
    user_id: str
    content: str
    event_type: str = "message" # message, environment, tick

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

### 2.2 接口抽象 (Abstract Interfaces)

#### `io` 模块接口
```python
from abc import ABC, abstractmethod

class InputAdapter(ABC):
    @abstractmethod
    async def receive(self) -> UserInput:
        """接收外部输入，转化为系统标准 UserInput"""
        pass

class OutputAdapter(ABC):
    @abstractmethod
    async def render(self, output: FinalOutput) -> None:
        """将过滤后的最终输出渲染展示给外部"""
        pass
```

#### `box` 模块接口
```python
class IStatusGuard(ABC):
    @abstractmethod
    def check_status(self, current_status: AgentStatus, user_input: UserInput) -> tuple[bool, Optional[FinalOutput]]:
        """检查状态。返回 (是否允许进入Agent层, 拦截时的系统代回内容)"""
        pass

class ISensoryGenerator(ABC):
    @abstractmethod
    def generate_sensory_data(self, user_input: UserInput, environment_context: dict) -> str:
        """将输入和环境合成感官文本"""
        pass

class IPrivacyFilter(ABC):
    @abstractmethod
    def filter_output(self, agent_action: AgentAction, current_status: AgentStatus) -> FinalOutput:
        """剔除内部思考，仅保留外显行为"""
        pass
```

#### `memory` 模块接口
```python
class IShortTermMemory(ABC):
    @abstractmethod
    async def add_memory(self, content: str, importance: float):
        pass
        
    @abstractmethod
    async def get_recent_memories(self, limit: int = 10) -> List[str]:
        pass
        
    @abstractmethod
    async def decay_and_cleanup(self, threshold_tokens: int):
        """执行时间衰减与清理"""
        pass

class ILongTermMemory(ABC):
    @abstractmethod
    async def store_fact(self, fact: str, embedding: List[float]):
        pass
        
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[str]:
        pass
```

#### `graph` 状态定义 (State)
```python
from typing import TypedDict

class AgentState(TypedDict):
    user_input: UserInput           # 原始输入
    current_status: AgentStatus     # 当前系统状态
    sensory_memory: str             # 合成的即时感官记忆
    retrieved_ltm: List[str]        # RAG检索到的长期记忆
    stm_context: List[str]          # 加载的短期记忆上下文
    agent_action: AgentAction       # LLM生成的原始动作(含内心独白)
    final_output: FinalOutput       # 过滤后的最终输出(如果被Box拦截则直接赋值)
```

## 3. 设计约定与参考指南

1. **接口先行原则**：后续各个模块（IO, Box, Memory, Agent, Graph）的详细设计文档，必须以上述定义的接口和职责为基准进行展开。
2. **偏差记录**：如果在后续子模块的详细设计过程中，发现本总体规划中的接口定义无法满足需求（如参数缺失、异步设计不合理等），**不可直接在此文档中隐瞒修改**。必须在具体子模块的详细设计文档中，设立专门的“与总体规划的偏差与修正”章节，说明违背的原因及新的设计方案，以供第二轮系统整体架构评审与调整使用。
