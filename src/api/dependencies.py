from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..config import get_settings
from ..llm import create_qwen_provider, BaseLLMProvider
from ..vector_store import create_chroma_vector_store, BaseVectorStore
from ..rag import create_rag_engine, RAGEngine, CharacterProfile


# 全局单例
_llm_provider: BaseLLMProvider = None
_vector_store: BaseVectorStore = None
_rag_engine: RAGEngine = None


def get_llm_provider() -> BaseLLMProvider:
    """获取 LLM 提供商单例"""
    global _llm_provider
    if _llm_provider is None:
        settings = get_settings()
        _llm_provider = create_qwen_provider(
            api_key=settings.qwen_api_key,
            chat_model=settings.qwen_chat_model,
            embed_model=settings.qwen_embed_model,
            base_url=settings.qwen_chat_base,
            embed_dim=settings.embed_dim,
        )
    return _llm_provider


def get_vector_store() -> BaseVectorStore:
    """获取向量存储单例"""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        _vector_store = create_chroma_vector_store(
            persist_dir=settings.chroma_persist_dir,
            collection_name=settings.chroma_collection_name,
            embedding_dim=settings.embed_dim,
        )
    return _vector_store


def get_rag_engine() -> RAGEngine:
    """获取 RAG 引擎单例"""
    global _rag_engine
    if _rag_engine is None:
        settings = get_settings()
        llm_provider = get_llm_provider()
        vector_store = get_vector_store()
        
        character_profile = CharacterProfile(
            name=settings.character_name,
            era=settings.character_era,
            personality=settings.character_personality,
            speaking_style=settings.character_speaking_style,
            background=settings.character_background.format(character_name=settings.character_name),
        )
        
        _rag_engine = create_rag_engine(
            llm_provider=llm_provider,
            vector_store=vector_store,
            character_profile=character_profile,
            top_k=5,
            use_character_mode=True,
        )
    return _rag_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时
    print(" Starting up...")
    settings = get_settings()
    print(f"   Character: {settings.character_name}")
    print(f"   Vector Store: {settings.vector_store_type}")
    
    yield
    
    # 关闭时
    print(" Shutting down...")
    global _llm_provider
    if _llm_provider:
        await _llm_provider.close()
    print(" Cleanup complete")