"""配置管理器"""
import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class AssistantConfig(BaseModel):
    """助手配置"""
    name: str = Field(..., description="助手名称")
    description: str = Field(..., description="助手描述")
    model: str = Field(default="qwen-plus", description="LLM 模型")
    temperature: float = Field(default=0.7, description="生成温度")
    max_tokens: int = Field(default=2000, description="最大 token 数")
    top_p: float = Field(default=0.95, description="top_p 参数")


class KnowledgeBaseConfig(BaseModel):
    """知识库配置"""
    id: str = Field(..., description="知识库 ID")
    name: str = Field(..., description="知识库名称")
    chunk_size: int = Field(default=1000, description="分块大小")
    chunk_overlap: int = Field(default=200, description="分块重叠")


class VectorStoreConfig(BaseModel):
    """向量存储配置"""
    type: str = Field(default="chromadb", description="向量存储类型")
    persist_dir: str = Field(default="./data/vector", description="持久化目录")
    collection_name: str = Field(..., description="集合名称")


class APIConfig(BaseModel):
    """API 配置"""
    port: int = Field(default=8000, description="API 端口")
    cors: bool = Field(default=True, description="是否启用 CORS")
    rate_limit: int = Field(default=1000, description="速率限制")


class MonitoringConfig(BaseModel):
    """监控配置"""
    enabled: bool = Field(default=True, description="是否启用监控")
    metrics_port: int = Field(default=9000, description="指标端口")


class Config(BaseModel):
    """系统配置"""
    assistant: AssistantConfig
    knowledge_base: KnowledgeBaseConfig
    vector_store: VectorStoreConfig
    api: APIConfig = APIConfig()
    monitoring: MonitoringConfig = MonitoringConfig()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件存储目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_config(self, kb_metadata: Dict[str, Any], assistant_name: str, assistant_description: str) -> Dict[str, Any]:
        """
        根据知识库元数据生成配置
        
        Args:
            kb_metadata: 知识库元数据
            assistant_name: 助手名称
            assistant_description: 助手描述
            
        Returns:
            生成的配置
        """
        # 生成向量存储集合名称
        import uuid
        collection_name = f"kb_{str(uuid.uuid4())[:8]}"
        
        # 创建配置
        config = {
            "assistant": {
                "name": assistant_name,
                "description": assistant_description,
                "model": "qwen-plus",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.95
            },
            "knowledge_base": {
                "id": kb_metadata.get("id", str(uuid.uuid4())[:8]),
                "name": kb_metadata.get("name", "Unknown Knowledge Base"),
                "chunk_size": kb_metadata.get("chunk_size", 1000),
                "chunk_overlap": kb_metadata.get("chunk_overlap", 200)
            },
            "vector_store": {
                "type": "chromadb",
                "persist_dir": "./data/vector",
                "collection_name": collection_name
            },
            "api": {
                "port": 8000,
                "cors": True,
                "rate_limit": 1000
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9000
            }
        }
        
        return config
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            if config_path.suffix.lower() == ".json":
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            elif config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
        except Exception as e:
            raise Exception(f"加载配置文件时出错: {str(e)}")
    
    def save_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            config_path: 配置文件路径
            
        Returns:
            是否保存成功
        """
        config_path = Path(config_path)
        
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.suffix.lower() == ".json":
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            elif config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
            
            return True
        except Exception:
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置的有效性
        
        Args:
            config: 配置字典
            
        Returns:
            验证结果，包含是否有效和错误信息
        """
        try:
            # 使用 Pydantic 验证配置
            Config(**config)
            return {
                "valid": True,
                "config": config
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置
        """
        import uuid
        return {
            "assistant": {
                "name": "Default Assistant",
                "description": "默认助手",
                "model": "qwen-plus",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.95
            },
            "knowledge_base": {
                "id": str(uuid.uuid4())[:8],
                "name": "Default Knowledge Base",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "vector_store": {
                "type": "chromadb",
                "persist_dir": "./data/vector",
                "collection_name": f"kb_{str(uuid.uuid4())[:8]}"
            },
            "api": {
                "port": 8000,
                "cors": True,
                "rate_limit": 1000
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9000
            }
        }
