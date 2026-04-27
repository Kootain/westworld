from src.memory.stm import STMManager
from src.memory.ltm import LTMManager
from src.core.config import settings
from typing import List
from src.memory.models import MemoryNode

class MemoryFacade:
    def __init__(self):
        self.stm = STMManager()
        self.ltm = LTMManager(settings.MILVUS_URI)

    def add_stm(self, content: str, importance: float, timestamp: float) -> None:
        self.stm.add_memory(content, importance, timestamp)

    def get_active_stm(self, current_time: float, threshold: float = 0.5) -> List[MemoryNode]:
        return self.stm.get_active_memories(current_time, threshold)

    def get_all_stm_content(self) -> str:
        return "\n".join([node.content for node in self.stm.nodes])

    def prune_stm(self, current_time: float) -> None:
        self.stm.prune_memories(current_time)

    def save_ltm(self, content: str) -> None:
        self.ltm.save(content)

    def retrieve_ltm(self, query: str, top_k: int = 5) -> List[str]:
        return self.ltm.retrieve(query, top_k)
