"""万能问答框架 API 服务"""
from datetime import datetime
import logging
import os
from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..core.knowledge.manager import KnowledgeBaseManager
from ..core.config.manager import ConfigManager
from ..core.task.scheduler import TaskScheduler, TaskType
from .file_upload_fixed import router as file_upload_router


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="万能问答框架 API",
    description="基于 FastAPI 的万能问答框架 API",
    version="1.0.0",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="./app/ui/static"), name="static")

# 包含文件上传路由
app.include_router(file_upload_router)

# 初始化管理器
kb_manager = KnowledgeBaseManager()
config_manager = ConfigManager()
task_scheduler = TaskScheduler()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径"""
    # 使用绝对路径
    current_dir = Path(__file__).parent.parent
    index_path = current_dir / "ui" / "static" / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return {
            "message": "万能问答框架 API",
            "version": "1.0.0",
            "docs": "/docs",
        }


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }


# 知识库管理接口

@app.post("/api/knowledge-bases/validate", response_model=Dict[str, Any])
async def validate_knowledge_base(kb_path: str):
    """验证知识库格式"""
    try:
        result = kb_manager.validate_knowledge_base(kb_path)
        return result
    except Exception as e:
        logger.error(f"Error validating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases", response_model=Dict[str, Any])
async def create_knowledge_base(
    files: List[UploadFile] = File(...),
    name: str = Form(...),
    description: str = Form(...),
    version: str = Form(default="1.0.0"),
    author: str = Form(default="Admin"),
):
    """创建知识库"""
    try:
        # 创建临时目录
        import tempfile
        import uuid
        temp_dir = tempfile.mkdtemp()
        kb_id = str(uuid.uuid4())[:8]
        kb_path = Path(temp_dir) / kb_id
        kb_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 metadata.json
        metadata = {
            "name": name,
            "description": description,
            "version": version,
            "created_at": datetime.now().isoformat(),
            "author": author,
            "embedding_model": "text-embedding-v4",
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
        metadata_path = kb_path / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 创建 documents 目录
        documents_path = kb_path / "documents"
        documents_path.mkdir(parents=True, exist_ok=True)
        
        # 保存上传的文件
        for file in files:
            file_path = documents_path / file.filename
            with open(file_path, "wb") as f:
                f.write(await file.read())
        
        # 处理知识库
        task_id = task_scheduler.create_task(
            TaskType.KNOWLEDGE_BASE_PROCESSING,
            {
                "kb_path": str(kb_path),
                "config": {}
            }
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "知识库处理任务已创建"
        }
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases", response_model=List[Dict[str, Any]])
async def list_knowledge_bases():
    """列出所有知识库"""
    try:
        knowledge_bases = kb_manager.list_knowledge_bases()
        return knowledge_bases
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases/{kb_id}", response_model=Dict[str, Any])
async def get_knowledge_base(kb_id: str):
    """获取知识库信息"""
    try:
        kb_info = kb_manager.get_knowledge_base(kb_id)
        if not kb_info:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        return kb_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge-bases/{kb_id}", response_model=Dict[str, Any])
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    try:
        success = kb_manager.delete_knowledge_base(kb_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        return {"success": True, "message": "Knowledge base deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 任务管理接口

@app.get("/api/tasks", response_model=List[Dict[str, Any]])
async def list_tasks(status: str = None):
    """列出任务"""
    try:
        from ..core.task.scheduler import TaskStatus
        task_status = TaskStatus(status) if status else None
        tasks = task_scheduler.list_tasks(task_status)
        return tasks
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: str):
    """获取任务状态"""
    try:
        result = task_scheduler.get_task_status(task_id)
        if not result["found"]:
            raise HTTPException(status_code=404, detail="Task not found")
        return result["task"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(task_id: str):
    """取消任务"""
    try:
        success = task_scheduler.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        return {"success": True, "message": "Task cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 助手管理接口

@app.post("/api/assistants", response_model=Dict[str, Any])
async def create_assistant(
    name: str = Form(...),
    description: str = Form(...),
    knowledge_base_id: str = Form(...),
):
    """创建助手"""
    try:
        # 获取知识库信息
        kb_info = kb_manager.get_knowledge_base(knowledge_base_id)
        if not kb_info:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # 生成配置
        config = config_manager.generate_config(
            kb_info,
            name,
            description
        )
        
        # 保存配置
        import uuid
        assistant_id = str(uuid.uuid4())[:8]
        config_path = Path("./config") / f"assistant_{assistant_id}.json"
        config_manager.save_config(config, str(config_path))
        
        return {
            "success": True,
            "assistant_id": assistant_id,
            "config": config,
            "message": "助手创建成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assistant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assistants", response_model=List[Dict[str, Any]])
async def list_assistants():
    """列出所有助手"""
    try:
        assistants = []
        config_dir = Path("./config")
        for config_file in config_dir.glob("assistant_*.json"):
            try:
                config = config_manager.load_config(str(config_file))
                assistant_id = config_file.stem.replace("assistant_", "")
                assistants.append({
                    "id": assistant_id,
                    "name": config.get("assistant", {}).get("name"),
                    "description": config.get("assistant", {}).get("description"),
                    "knowledge_base_id": config.get("knowledge_base", {}).get("id"),
                    "created_at": config_file.stat().st_ctime
                })
            except Exception:
                pass
        return assistants
    except Exception as e:
        logger.error(f"Error listing assistants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assistants/{assistant_id}", response_model=Dict[str, Any])
async def get_assistant(assistant_id: str):
    """获取助手信息"""
    try:
        config_path = Path("./config") / f"assistant_{assistant_id}.json"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Assistant not found")
        config = config_manager.load_config(str(config_path))
        return {
            "id": assistant_id,
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assistant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/assistants/{assistant_id}", response_model=Dict[str, Any])
async def delete_assistant(assistant_id: str):
    """删除助手"""
    try:
        config_path = Path("./config") / f"assistant_{assistant_id}.json"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Assistant not found")
        config_path.unlink()
        return {"success": True, "message": "Assistant deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assistant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 聊天接口

@app.post("/api/assistants/{assistant_id}/chat", response_model=Dict[str, Any])
async def chat_with_assistant(assistant_id: str, request: Dict[str, Any]):
    """与助手聊天"""
    try:
        # 获取助手配置
        config_path = Path("./config") / f"assistant_{assistant_id}.json"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Assistant not found")
        config = config_manager.load_config(str(config_path))
        
        # 这里实现聊天逻辑
        # 暂时返回模拟响应
        message = request.get("message", "")
        return {
            "answer": f"这是对问题 '{message}' 的回答",
            "model": config.get("assistant", {}).get("model"),
            "sources": [],
            "usage": {
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error chatting with assistant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
