# Memory 模块详细设计方案

## 1. 模块职责与定位

`memory` 模块负责智能体三级记忆系统（STM, LTM）的管理，以及基于遗忘曲线的自动清理和异步固化（Consolidation）。
1. **短期记忆 (STM)**：基于 Redis 或本地内存/DB，保存近期的对话、行为及心理状态，带有重要性打分和时间戳。
2. **长期记忆 (LTM)**：基于向量数据库（如 Milvus / PGVector），存储核心设定和提炼后的长久事实。
3. **固化机制 (Consolidation)**：定期将 STM 中的重要信息提炼并持久化到 LTM 中。

*注：感官记忆 (Sensory Memory) 由于生命周期极短，不在此做持久化存储，而是直接作为 State 的变量在 Graph 中传递。*

## 2. 详细方案设计

### 2.1 记忆数据模型

在 `memory/models.py` 中定义内部数据结构：

```python
from pydantic import BaseModel
from typing import List

class MemoryFragment(BaseModel):
    id: str
    content: str
    importance: float     # 1.0 - 10.0
    timestamp: float      # 创建时的 Unix 时间戳
    token_count: int      # 占用的 Token 估算值
```

### 2.2 短期记忆组件 (`stm.py`)

实现 `IShortTermMemory` 接口。
- **职责**：维护滑动窗口内的记忆片段。
- **衰减算法**：$V = I \cdot e^{-\lambda(T_{now} - T_{created})}$。
- **清理逻辑**：当总体 `token_count` 超过配置阈值（如 4000）时，触发 `decay_and_cleanup`。按 $V$ 值从小到大排序，剔除最低价值的片段，直到总 Token 数回到安全水位。

### 2.3 长期记忆组件 (`ltm.py`)

实现 `ILongTermMemory` 接口。
- **职责**：包装对向量数据库的调用。
- **逻辑**：
  - `store_fact(fact, embedding)`: 存储事实向量。
  - `search(query, top_k)`: 使用 query 向量在库中进行相似度检索。

### 2.4 记忆固化服务 (`consolidation.py`)

- **职责**：定期执行的后台任务或在状态流转时（如睡前）触发。
- **逻辑**：
  1. 提取 STM 中最近未被固化过的一批记忆片段。
  2. 调用 LLM（使用摘要提炼 Prompt），将冗长的对话和心理活动提炼为“核心事实”和“关系变动”。
  3. 调用 Embedding 模型将其向量化，并写入 LTM。
  4. 标记或清理已固化的 STM 片段。

## 3. 与总体规划的偏差与修正

*偏差说明*：总体设计未详细指定 STM 的内部存储形式。详细设计中引入了 `MemoryFragment` 数据类来承载重要性与时间戳。为了确保系统的无状态性以便于水平扩展，STM 的实现建议初期采用 Redis List/ZSet 存储 `MemoryFragment` 的 JSON 序列化形式，而不是保存在 Python 进程内存中。
