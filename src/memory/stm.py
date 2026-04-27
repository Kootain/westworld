from typing import List
from src.memory.models import MemoryNode
from src.core.config import settings
from src.core.enums import MemoryType
import uuid

class STMManager:
    def __init__(self):
        self.nodes: List[MemoryNode] = []

    def add_memory(self, content: str, importance: float, timestamp: float) -> None:
        node = MemoryNode(
            id=str(uuid.uuid4()),
            content=content,
            mem_type=MemoryType.STM,
            importance=importance,
            created_at=timestamp,
            last_accessed_at=timestamp
        )
        self.nodes.append(node)

    def get_active_memories(self, current_time: float, threshold: float = 0.5) -> List[MemoryNode]:
        """
        返回衰减值（V）高于一定阈值的有效记忆，或者按衰减值排序的 Top-N。
        """
        active_nodes = []
        for node in self.nodes:
            decay_val = node.calculate_decay(current_time, settings.DECAY_RATE)
            if decay_val >= threshold:
                active_nodes.append(node)
        
        # 按衰减值从高到低排序
        active_nodes.sort(key=lambda n: n.calculate_decay(current_time, settings.DECAY_RATE), reverse=True)
        return active_nodes

    def prune_memories(self, current_time: float) -> None:
        """
        如果超过 Token 限制，则清理 V 值最低的片段。
        """
        self.nodes.sort(key=lambda n: n.calculate_decay(current_time, settings.DECAY_RATE), reverse=True)
        
        # 简单用字符长度近似模拟 Token 数
        current_tokens = 0
        keep_nodes = []
        for node in self.nodes:
            tokens = len(node.content) // 4 + 1
            if current_tokens + tokens <= settings.STM_TOKEN_LIMIT:
                keep_nodes.append(node)
                current_tokens += tokens
            else:
                break
        self.nodes = keep_nodes
