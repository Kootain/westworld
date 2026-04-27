from typing import List

class LTMManager:
    def __init__(self, db_uri: str):
        # 初始化向量数据库连接（如 Milvus）
        self.db_uri = db_uri
        self.storage: List[str] = []

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        # 向量化 Query 并查询相似记忆 (当前使用简单的文本匹配模拟)
        results = [m for m in self.storage if query.lower() in m.lower()]
        return results[:top_k]

    def save(self, content: str) -> None:
        # 将固化后的记忆存入 LTM
        self.storage.append(content)
