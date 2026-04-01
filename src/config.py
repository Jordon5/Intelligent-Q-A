import os
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """
    应用配置类，使用 Pydantic 进行类型安全的配置管理
    """

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    qwen_api_key: Optional[str] = None
    qwen_chat_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_embed_model: str = "text-embedding-v4"
    qwen_chat_model: str = "qwen-plus"
    embed_dim: int = 1024

    # 向量数据库
    vector_store_type: str = "chroma"
    chroma_persist_dir: Path = Path("./data/chroma")
    chroma_collection_name: str = "rag_collection"

    # 数字分身
    character_name: str = "Unknown Character"
    character_dir: Path = Path('./character-knowledge/')
    character_era: str = "Unknown Era"
    character_personality: str = "温和儒雅，胸有丘壑，悲天悯人"
    character_speaking_style: str = "言语温和，引经据典，有教书先生的儒雅气质"
    character_background: str = "文圣弟子，曾任山崖书院山主，是{character_name}的启蒙恩师"

    # 数据摄入
    chunk_size: int = 600
    chunk_overlap: int = 50
    max_concurrent_ingest: int = 10

    # 日志
    log_level: str ="INFO"

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

# 全局配置实例
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """获取全局配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
        # 确保目录存在
        _settings.chroma_persist_dir.mkdir(
            parents=True,
            exist_ok=True
        )
    return _settings

