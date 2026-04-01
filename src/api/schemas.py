from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    history: List[Dict[str, str]] = Field(default=[], description="对话历史")
    language: str = Field(default="zh", description="语言 (zh/en)")


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str = Field(..., description="回答内容")
    sources: List[Dict[str, Any]] = Field(default=[], description="来源信息")
    used_fallback: bool = Field(default=False, description="是否使用回退")
    model: Optional[str] = Field(default=None, description="使用的模型")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Token 使用情况")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok", description="服务状态")
    version: str = Field(default="1.0.0", description="版本号")
    timestamp: str = Field(..., description="当前时间")


class VectorStatsResponse(BaseModel):
    """向量库统计"""
    total_documents: int = Field(..., description="文档总数")
    collection_name: str = Field(..., description="集合名称")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    details: Optional[str] = Field(default=None, description="详细错误信息")