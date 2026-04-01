from datetime import datetime
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ..config import get_settings
from ..rag import RAGResponse
from .schemas import ChatRequest, ChatResponse, HealthResponse, VectorStatsResponse, ErrorResponse
from .dependencies import lifespan, get_rag_engine, get_vector_store


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="数字分身 RAG API",
    description="基于 FastAPI 的数字分身聊天机器人 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )


@app.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/stats", response_model=VectorStatsResponse)
async def get_stats():
    """获取向量库统计"""
    try:
        vector_store = get_vector_store()
        count = await vector_store.count()
        settings = get_settings()
        
        return VectorStatsResponse(
            total_documents=count,
            collection_name=settings.chroma_collection_name,
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        logger.info(f"Chat request: {request.message[:50]}...")
        
        rag_engine = get_rag_engine()
        response = await rag_engine.chat(
            message=request.message,
            history=request.history,
            language=request.language,
        )
        
        return ChatResponse(
            answer=response.answer,
            sources=response.sources,
            used_fallback=response.used_fallback,
            model=response.model,
            usage=response.usage,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info")
async def get_info():
    """获取服务信息"""
    settings = get_settings()
    return {
        "character_name": settings.character_name,
        "character_era": settings.character_era,
        "vector_store_type": settings.vector_store_type,
        "llm_model": settings.qwen_chat_model,
        "embed_model": settings.qwen_embed_model,
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )