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
