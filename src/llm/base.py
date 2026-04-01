"""LLM 抽象基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Message:
    """消息基类"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}
    
class ChatResponse:
    """聊天响应基类"""
    def __init__(self, content: str, model: str, usage: Optional[Dict[str,int]] = None):
        self.content = content
        self.model = model
        self.usage = usage
    
class EmbeddingResponse:
    """嵌入响应基类"""
    def __init__(self, embeddings: List[float], model: str, usage: Optional[Dict[str, int]] = None):
        self.embeddings = embeddings
        self.model = model
        self.usage = usage

class BaseLLMProvider(ABC):
    """LLM 提供商抽象基类"""

    @abstractmethod
    async def chat(self, messages: List[Message], temperature: float = 0.7, max_tokens: int = 1024) -> ChatResponse:
        """
        聊天生成

        Args:
            messages: 消息列表
            temperature: 生成温度
            max_tokens: 最大 tokens

        Returns:
            聊天响应
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> EmbeddingResponse:
        """
        文本嵌入

        Args:
            texts: 文本列表

        Returns:
            嵌入响应
        """
        pass

    @abstractmethod
    def get_embed_dim(self) -> int:
        """
        获取嵌入维度

        Returns:
            嵌入维度
        """
        pass

    @abstractmethod
    async def close(self) -> str:
        """
        关闭资源
        """
        pass