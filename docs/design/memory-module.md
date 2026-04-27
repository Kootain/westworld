# Memory 模块详细设计文档

## 1. 模块职责
`memory` 模块是系统中负责数据持久化、上下文维持和记忆演进的核心组件。
它的主要职责包括：
1. **Sensory Memory (感官记忆)**：临时缓存，生命周期极短。
2. **Short-Term Memory (STM, 短期记忆)**：工作内存，带有重要性（Importance）和时间衰减算法（Decay）。
3. **Long-Term Memory (LTM, 长期记忆)**：核心事实库，基于向量数据库进行语义检索。
4. **记忆固化 (Consolidation)**：定期将 STM 提炼并写入 LTM。

## 2. 详细设计

### 2.1 内部数据模型 (`src/memory/models.py`)
在 `core` 模块反思中，我们确定了仅内部使用的模型应放在对应模块中。因此在 `memory` 内部定义：

```python
from pydantic import BaseModel, Field
from src.core.enums import MemoryType

class MemoryNode(BaseModel):
    """
    统一的记忆片段结构
    """
    id: str
    content: str
    mem_type: MemoryType
    importance: float = 1.0
    created_at: float
    last_accessed_at: float
    
    def calculate_decay(self, current_time: float, decay_rate: float) -> float:
        import math
        return self.importance * math.exp(-decay_rate * (current_time - self.created_at))
```

### 2.2 短期记忆管理器 (`src/memory/stm.py`)
负责管理工作内存，包含添加、读取、清理过载和衰减的逻辑：

```python
from typing import List
from src.memory.models import MemoryNode
from src.core.config import settings

class STMManager:
    def __init__(self):
        self.nodes: List[MemoryNode] = []
        
    def add_memory(self, content: str, importance: float, timestamp: float) -> None:
        pass
        
    def get_active_memories(self, current_time: float) -> List[MemoryNode]:
        """
        返回衰减值（V）高于一定阈值的有效记忆，或者按衰减值排序的 Top-N。
        """
        pass
        
    def prune_memories(self, current_time: float) -> None:
        """
        如果超过 Token 限制，则清理 V 值最低的片段。
        """
        pass
```

### 2.3 长期记忆与检索 (`src/memory/ltm.py`)
封装向量数据库的读写：

```python
class LTMManager:
    def __init__(self, db_uri: str):
        # 初始化向量数据库连接（如 Milvus）
        pass
        
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        # 向量化 Query 并查询相似记忆
        pass
        
    def save(self, content: str) -> None:
        # 将固化后的记忆存入 LTM
        pass
```

### 2.4 记忆门面类 (`src/memory/facade.py`)
为了给上层（`agent`, `box`, `graph`）提供统一接口，使用 Facade 模式：

```python
class MemoryFacade:
    def __init__(self):
        self.stm = STMManager()
        self.ltm = LTMManager(settings.MILVUS_URI)
        
    # 提供统一的 API
```

## 3. 设计冲突与违背

在详细设计时，我们发现了一个与 `docs/system-design.md` 中的小分歧：
- **冲突描述**：初期设计中规定“系统需定期（如每 20 轮对话，或在进入睡觉状态时）触发后台任务，调用 LLM 对 STM 进行提炼”。
- **违背处理**：`memory` 模块本身不包含 LLM 调用的逻辑，因为 `memory` 的职责是“存储引擎封装”。因此，“调用 LLM 提炼记忆”的职责（Consolidation）被设计为由上层 `graph` 触发，或者放在 `agent` 模块的特定节点中（比如 `ConsolidateNode`），然后 `graph`/`agent` 将提炼结果通过 `MemoryFacade.save_ltm()` 写入。
- **结论**：我们将 `Consolidation` 逻辑从 `memory` 的内部算法中剥离出来，只在 `memory` 提供存取 API。

## 4. 设计反思

**反思结论：**
1. **职责边界更清晰**：把带有 LLM 调用的“提炼”动作从底层存储层 (`memory`) 移动到认知层 (`agent` / `graph`) 是正确的。底层只管存储结构和衰减公式，不关心怎么总结大纲。
2. **依赖传递**：在后续 `agent` 模块设计中，需要增加一个专门的 `ConsolidationNode` 或 `ReflectionNode` 来处理“总结 STM 写入 LTM”的逻辑。
3. **接口扩展**：`MemoryFacade` 需要向外暴露 `get_all_stm_content()`，以便上层在进行固化时能拿到完整的上下文去调用 LLM。
