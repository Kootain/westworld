# 整体架构与接口设计文档

## 1. 架构概述

LangGraph RPG-Agent 系统采用领域驱动设计（DDD）思想，将系统分为三个核心层级：
1. **持久化层 (Memory Layer)**：处理系统和角色的记忆、状态持久化。
2. **系统层 (Box Layer)**：系统容器，负责输入拦截、感官合成及隐私过滤，代表了世界的“物理法则”。
3. **认知层 (Agent Layer)**：作为纯粹的认知和决策单元运行，基于 LangGraph 的 Sub-Graph。

为了实现各层级的解耦与协作，系统拆分为以下 6 个核心模块，并按依赖关系严格管理：`core`, `io`, `memory`, `agent`, `box`, `graph`。

## 2. 模块职责规划

### 2.1 core 模块
- **职责**：系统地基。提供全局配置（Config）、基础数据模型（Pydantic Models）和通用工具类（Utils）。
- **边界**：不包含任何业务逻辑，被所有其他模块依赖。

### 2.2 io 模块
- **职责**：负责系统的输入与输出。通过插件化适配器（Adapter）实现与外部系统（Console, Web, Game Client）的通信解耦。
- **边界**：不感知具体的业务流程，只负责接收字符串输入和展示标准化输出。

### 2.3 memory 模块
- **职责**：管理三级记忆（感官记忆、短期记忆 STM、长期记忆 LTM）以及记忆的遗忘与固化机制。
- **边界**：封装底层存储引擎（Redis/PG/Milvus 等），对外暴露增删改查及衰减计算的 API，不涉及具体的 Agent 认知推演。

### 2.4 agent 模块
- **职责**：实现智能体的核心认知闭环（感知、联想、思考、行为）。封装 Prompt 模板和与 LLM 的交互。
- **边界**：不直接读取数据库，而是调用 `memory` 模块的接口获取上下文；不直接输出到终端，而是生成结构化的 JSON 数据。

### 2.5 box 模块
- **职责**：作为系统的“守卫”。在输入阶段拦截不合理的交互（如睡眠状态），合成环境感官数据；在输出阶段剔除 Agent 的内心独白（SoT），保护隐私。
- **边界**：控制流的最高优先级节点，协调 `io` 和 `agent` 之间的信息传递，依赖 `memory` 获取环境状态。

### 2.6 graph 模块
- **职责**：系统的工作流总线。基于 LangGraph 组装上述模块，定义全局 State 的流转。
- **边界**：作为组装层，不包含具体的业务实现，仅负责节点（Node）和边（Edge）的调度与编排。

## 3. 核心接口设计

为了保证解耦，需定义以下核心接口（后续各模块设计需遵循）：

### 3.1 状态与数据模型 (core)
```python
from pydantic import BaseModel
from typing import Optional

class AgentStatus(str, Enum):
    NORMAL = "NORMAL"
    SLEEPING = "SLEEPING"
    WORKING = "WORKING"
    UNCONSCIOUS = "UNCONSCIOUS"

class AgentResponse(BaseModel):
    Speech: Optional[str]
    Action: Optional[str]
    SoT: str
    Status_Change: Optional[AgentStatus]
```

### 3.2 I/O 适配器接口 (io)
```python
from abc import ABC, abstractmethod

class InputAdapter(ABC):
    @abstractmethod
    async def receive(self) -> str:
        pass

class OutputAdapter(ABC):
    @abstractmethod
    async def render(self, speech: str, action: str) -> None:
        pass
```

### 3.3 记忆系统接口 (memory)
```python
from abc import ABC, abstractmethod

class MemoryManager(ABC):
    @abstractmethod
    async def add_stm(self, content: str, importance: float) -> None:
        pass
        
    @abstractmethod
    async def retrieve_ltm(self, query: str, top_k: int = 5) -> list[str]:
        pass
```

## 4. 模块依赖关系

系统采用单向依赖链，避免循环依赖：
```mermaid
graph TD
    core[core 模块]
    io[io 模块]
    memory[memory 模块]
    agent[agent 模块]
    box[box 模块]
    graph[graph 模块]

    io --> core
    memory --> core
    agent --> memory
    agent --> core
    box --> memory
    box --> io
    box --> core
    graph --> box
    graph --> agent
    graph --> memory
    graph --> io
    graph --> core
```

**设计反思机制说明**：
在后续详细设计中，我们将严格按照 `core -> io -> memory -> agent -> box -> graph` 的顺序进行。每个模块设计完成后，需记录反思（如接口是否需要调整、是否遗漏了必要的上下文），并向下传递给下一个模块。
