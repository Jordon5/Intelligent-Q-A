"""向量存储基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorDocument:
    """向量文档"""
    def __init__(self, id: str, text: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.text = text
        self.vector = vector
        self.metadata = metadata or {}


class SearchResult:
    """搜索结果"""
    def __init__(self, documents: VectorDocument, score: float):
        self.documents = documents
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.documents.text,
            "score": self.score,
            "metadata": self.documents.metadata,
        }
    

class BaseVectorStore(ABC):
    """向量存储基类"""
    @abstractmethod
    async def add_documents(self, documents: List[VectorDocument]):
        """
        添加文档

        Args:
            documents: 文档列表
        """
        pass

    @abstractmethod
    async def search(self, query_vector: List[float], top_k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[SearchResult]: 
        pass

    @abstractmethod
    async def delete_documents(self, ids: List[str]):
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

        