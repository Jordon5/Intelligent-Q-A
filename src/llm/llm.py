import httpx
from typing import List, Dict, Any, Optional

from .base import BaseLLMProvider, Message, ChatResponse, EmbeddingResponse

class QwenLLMProvider(BaseLLMProvider):
    """
    Qwen 提供商
    """
    def __init__(
            self,
            api_key: str,
            chat_model: str = "qwen-plus",
            embed_model: str = "text-embedding-v4",
            base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
            embed_dim: int = 1024,
            ):
        super().__init__()
        self.api_key = api_key
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.base_url = base_url
        self.embed_dim = embed_dim
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat(self, messages: List[Message], temperature: float = 0.7, max_tokens: int = 1000) -> ChatResponse:
        """
        聊天生成
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.chat_model,
            "messages":[msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_token": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        model = data["model"]
        usage = data.get("usage")
        return ChatResponse(
            content=content,
            model=model,
            usage=usage,
        )
    
    async def embed(self, texts: List[str]) -> EmbeddingResponse:
        """
        文本嵌入
        """
        url = f"{self.base_url}/embeddings"

        payload = {
            "model": self.embed_model,
            "input": texts,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        embeddings = [item["embedding"] for item in data["data"]]
        model = data["model"]
        usage = data.get("usage")
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage=usage
        )
    
    def get_embed_dim(self):
        return self.embed_dim
    
    async def close(self):
        await self.client.aclose()
    
def create_qwen_provider(
        api_key: str,
        chat_model: str = "qwen-plus",
        embed_model: str = "text-embedding-v4",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        embed_dim: int = 1024,
) -> BaseLLMProvider:
    return QwenLLMProvider(
        api_key=api_key,
        chat_model=chat_model,
        embed_model=embed_model,
        base_url=base_url,
        embed_dim=embed_dim,
    )
        
    
