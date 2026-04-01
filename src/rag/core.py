"""RAG 核心引擎"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..llm import BaseLLMProvider, Message
from ..vector_store import BaseVectorStore, SearchResult
from .prompt import build_character_prompt, build_basic_prompt, CharacterProfile


@dataclass
class RAGResponse:
    """RAG 响应"""
    def __init__(
        self,
        answer: str,
        sources: List[Dict[str, Any]] = None,
        used_fallback: bool = False,
        model: str = None,
        usage: Dict[str, Any] = None,
    ):
        self.answer = answer
        self.sources = sources or []
        self.used_fallback = used_fallback
        self.model = model
        self.usage = usage


class RAGEngine:
    """RAG 引擎"""
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        vector_store: BaseVectorStore,
        character_profile: Optional[CharacterProfile] = None,
        top_k: int = 5,
        use_character_mode: bool = False,
    ):
        """
        初始化 RAG 引擎
        
        Args:
            llm_provider: LLM 提供商
            vector_store: 向量存储
            character_profile: 人物配置
            top_k: 检索结果数量
            use_character_mode: 是否使用人物模式
        """
        self.llm_provider = llm_provider
        self.vector_store = vector_store
        self.character_profile = character_profile
        self.top_k = top_k
        self.use_character_mode = use_character_mode
        self.logger = logging.getLogger(__name__)
    
    async def chat(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        language: str = "zh",
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGResponse:
        """
        聊天接口
        
        Args:
            message: 用户消息
            history: 对话历史
            language: 语言
            filter_metadata: 元数据过滤
            
        Returns:
            RAG 响应
        """
        history = history or []
        
        try:
            # 1. 生成查询向量
            self.logger.info(f"Generating embedding for query: {message[:50]}...")
            embed_response = await self.llm_provider.embed([message])
            query_vector = embed_response.embeddings[0]
            
            # 2. 向量检索
            self.logger.info(f"Searching for relevant documents (top_k={self.top_k})")
            search_results = await self.vector_store.search(
                query_vector=query_vector,
                top_k=self.top_k,
                filter_metadata=filter_metadata,
            )
            
            # 3. 格式化上下文
            contexts = [result.documents.text for result in search_results]
            sources = [result.to_dict() for result in search_results]
            
            # 4. 构建提示词
            if self.use_character_mode and self.character_profile:
                prompt = build_character_prompt(
                    character_profile=self.character_profile,
                    context=contexts,
                    history=history,
                    question=message,
                    language=language,
                )
            else:
                prompt = build_basic_prompt(
                    contexts=contexts,
                    history=history,
                    question=message,
                    language=language,
                )
            
            # 5. LLM 生成回答
            self.logger.info("Generating answer with LLM")
            messages = [
                Message(role="system", content=prompt),
                Message(role="user", content=message),
            ]
            
            chat_response = await self.llm_provider.chat(messages)
            
            return RAGResponse(
                answer=chat_response.content,
                sources=sources,
                used_fallback=False,
                model=chat_response.model,
                usage=chat_response.usage,
            )
            
        except Exception as e:
            self.logger.error(f"RAG chat error: {e}", exc_info=True)
            
            # 回退机制
            fallback_prompt = "无法处理您的请求，请稍后再试。"
            if self.use_character_mode and self.character_profile:
                fallback_prompt = f"抱歉，{self.character_profile.name}暂时无法回答您的问题，请稍后再试。"
            
            return RAGResponse(
                answer=fallback_prompt,
                sources=[],
                used_fallback=True,
            )
    
    async def ask(
        self,
        question: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGResponse:
        """
        单次提问接口
        
        Args:
            question: 问题
            filter_metadata: 元数据过滤
            
        Returns:
            RAG 响应
        """
        return await self.chat(
            message=question,
            history=[],
            filter_metadata=filter_metadata,
        )


def create_rag_engine(
    llm_provider: BaseLLMProvider,
    vector_store: BaseVectorStore,
    character_profile: Optional[CharacterProfile] = None,
    top_k: int = 5,
    use_character_mode: bool = False,
) -> RAGEngine:
    """
    创建 RAG 引擎实例
    
    Args:
        llm_provider: LLM 提供商
        vector_store: 向量存储
        character_profile: 人物配置
        top_k: 检索结果数量
        use_character_mode: 是否使用人物模式
        
    Returns:
        RAG 引擎实例
    """
    return RAGEngine(
        llm_provider=llm_provider,
        vector_store=vector_store,
        character_profile=character_profile,
        top_k=top_k,
        use_character_mode=use_character_mode,
    )