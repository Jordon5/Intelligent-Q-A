"""文件上传和断点续传 API"""
import os
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import aiofiles
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse

# 根据环境选择配置
import os
if os.getenv('DEV_MODE') == 'true':
    from ..core.tasks.celery_config_dev import celery_app
else:
    from ..core.tasks.celery_config import celery_app

from ..core.tasks.celery_tasks import process_knowledge_base_task


logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/files", tags=["文件管理"])

# 临时文件存储目录
TEMP_UPLOAD_DIR = Path("./data/temp_uploads")
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """
    计算文件的 MD5 哈希值
    
    Args:
        file_path: 文件路径
        chunk_size: 块大小
        
    Returns:
        文件哈希值
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def get_upload_session_dir(session_id: str) -> Path:
    """
    获取上传会话目录
    
    Args:
        session_id: 会话 ID
        
    Returns:
        上传会话目录
    """
    session_dir = TEMP_UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


@router.post("/upload/init")
async def init_upload_session(
    file_name: str = Form(...),
    file_size: int = Form(...),
    file_hash: Optional[str] = Form(None),
    chunk_size: int = Form(5 * 1024 * 1024)  # 默认 5MB
):
    """
    初始化上传会话
    
    Args:
        file_name: 文件名
        file_size: 文件大小
        file_hash: 文件哈希值（可选）
        chunk_size: 分块大小
        
    Returns:
        会话信息
    """
    import uuid
    
    session_id = str(uuid.uuid4())
    session_dir = get_upload_session_dir(session_id)
    
    # 保存会话信息
    session_info = {
        "session_id": session_id,
        "file_name": file_name,
        "file_size": file_size,
        "file_hash": file_hash,
        "chunk_size": chunk_size,
        "uploaded_chunks": [],
        "total_chunks": (file_size + chunk_size - 1) // chunk_size
    }
    
    session_file = session_dir / "session_info.json"
    import json
    async with aiofiles.open(session_file, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(session_info, ensure_ascii=False, indent=2))
    
    return JSONResponse(content=session_info)


@router.post("/upload/chunk")
async def upload_chunk(
    session_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk_data: UploadFile = File(...),
    chunk_hash: Optional[str] = Form(None)
):
    """
    上传文件块
    
    Args:
        session_id: 会话 ID
        chunk_index: 块索引
        chunk_data: 块数据
        chunk_hash: 块哈希值（可选）
        
    Returns:
        上传结果
    """
    session_dir = get_upload_session_dir(session_id)
    session_file = session_dir / "session_info.json"
    
    # 检查会话是否存在
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # 读取会话信息
    import json
    async with aiofiles.open(session_file, 'r', encoding='utf-8') as f:
        session_info = json.loads(await f.read())
    
    # 检查块索引是否有效
    if chunk_index < 0 or chunk_index >= session_info["total_chunks"]:
        raise HTTPException(status_code=400, detail=f"Invalid chunk index: {chunk_index}")
    
    # 检查块是否已上传
    if chunk_index in session_info["uploaded_chunks"]:
        return JSONResponse(content={
            "status": "already_uploaded",
            "message": f"Chunk {chunk_index} already uploaded"
        })
    
    # 保存块数据
    chunk_file = session_dir / f"chunk_{chunk_index}.tmp"
    async with aiofiles.open(chunk_file, 'wb') as f:
        content = await chunk_data.read()
        await f.write(content)
    
    # 可选：验证块哈希
    if chunk_hash:
        calculated_hash = hashlib.md5(content).hexdigest()
        if calculated_hash != chunk_hash:
            # 删除无效的块
            chunk_file.unlink()
            raise HTTPException(status_code=400, detail="Chunk hash mismatch")
    
    # 更新会话信息
    session_info["uploaded_chunks"].append(chunk_index)
    async with aiofiles.open(session_file, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(session_info, ensure_ascii=False, indent=2))
    
    return JSONResponse(content={
        "status": "success",
        "chunk_index": chunk_index,
        "uploaded_chunks": len(session_info["uploaded_chunks"]),
        "total_chunks": session_info["total_chunks"]
    })


@router.post("/upload/complete")
async def complete_upload(session_id: str):
    """
    完成上传，合并所有块
    
    Args:
        session_id: 会话 ID
        
    Returns:
        合并结果
    """
    session_dir = get_upload_session_dir(session_id)
    session_file = session_dir / "session_info.json"
    
    # 检查会话是否存在
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # 读取会话信息
    import json
    async with aiofiles.open(session_file, 'r', encoding='utf-8') as f:
        session_info = json.loads(await f.read())
    
    # 检查是否所有块都已上传
    if len(session_info["uploaded_chunks"]) != session_info["total_chunks"]:
        raise HTTPException(
            status_code=400,
            detail=f"Not all chunks uploaded: {len(session_info['uploaded_chunks'])}/{session_info['total_chunks']}"
        )
    
    # 合并所有块
    final_file_path = session_dir / session_info["file_name"]
    async with aiofiles.open(final_file_path, 'wb') as f:
        for chunk_index in range(session_info["total_chunks"]):
            chunk_file = session_dir / f"chunk_{chunk_index}.tmp"
            if chunk_file.exists():
                async with aiofiles.open(chunk_file, 'rb') as chunk_f:
                    await f.write(await chunk_f.read())
    
    # 验证文件哈希（如果提供了）
    if session_info.get("file_hash"):
        calculated_hash = calculate_file_hash(final_file_path)
        if calculated_hash != session_info["file_hash"]:
            final_file_path.unlink()
            raise HTTPException(status_code=400, detail="File hash mismatch")
    
    # 验证文件大小
    actual_size = final_file_path.stat().st_size
    if actual_size != session_info["file_size"]:
        final_file_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"File size mismatch: expected {session_info['file_size']}, got {actual_size}"
        )
    
    # 清理临时块文件
    for chunk_index in range(session_info["total_chunks"]):
        chunk_file = session_dir / f"chunk_{chunk_index}.tmp"
        if chunk_file.exists():
            chunk_file.unlink()
    
    return JSONResponse(content={
        "status": "completed",
        "file_path": str(final_file_path),
        "file_name": session_info["file_name"],
        "file_size": actual_size
    })


@router.get("/upload/status/{session_id}")
async def get_upload_status(session_id: str):
    """
    获取上传状态
    
    Args:
        session_id: 会话 ID
        
    Returns:
        上传状态
    """
    session_dir = get_upload_session_dir(session_id)
    session_file = session_dir / "session_info.json"
    
    # 检查会话是否存在
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # 读取会话信息
    import json
    async with aiofiles.open(session_file, 'r', encoding='utf-8') as f:
        session_info = json.loads(await f.read())
    
    # 计算上传进度
    progress = (len(session_info["uploaded_chunks"]) / session_info["total_chunks"]) * 100
    
    return JSONResponse(content={
        "session_id": session_id,
        "file_name": session_info["file_name"],
        "file_size": session_info["file_size"],
        "uploaded_chunks": len(session_info["uploaded_chunks"]),
        "total_chunks": session_info["total_chunks"],
        "progress": round(progress, 2),
        "status": "uploading" if len(session_info["uploaded_chunks"]) < session_info["total_chunks"] else "completed"
    })


@router.delete("/upload/{session_id}")
async def cancel_upload(session_id: str):
    """
    取消上传，清理临时文件
    
    Args:
        session_id: 会话 ID
        
    Returns:
        取消结果
    """
    session_dir = get_upload_session_dir(session_id)
    
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # 清理所有临时文件
    import shutil
    shutil.rmtree(session_dir)
    
    return JSONResponse(content={
        "status": "cancelled",
        "session_id": session_id
    })


@router.post("/process-knowledge-base")
async def process_knowledge_base(
    file_path: str = Form(...),
    config: Optional[str] = Form(None)
):
    """
    处理知识库（异步任务）
    
    Args:
        file_path: 文件路径
        config: 配置（JSON 字符串）
        
    Returns:
        任务信息
    """
    import json
    
    # 解析配置
    task_config = json.loads(config) if config else {}
    
    # 提交 Celery 任务
    task = process_knowledge_base_task.delay(
        kb_path=file_path,
        config=task_config
    )
    
    return JSONResponse(content={
        "task_id": task.id,
        "status": "pending",
        "message": "Knowledge base processing task created"
    })


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务状态
    """
    # 获取 Celery 任务结果
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        status = "pending"
        result = None
    elif task_result.state == 'STARTED':
        status = "running"
        result = None
    elif task_result.state == 'SUCCESS':
        status = "completed"
        result = task_result.result
    elif task_result.state == 'FAILURE':
        status = "failed"
        result = {
            "error": str(task_result.info),
            "traceback": task_result.traceback
        }
    else:
        status = task_result.state
        result = None
    
    return JSONResponse(content={
        "task_id": task_id,
        "status": status,
        "result": result
    })


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务
    
    Args:
        task_id: 任务 ID
        
    Returns:
        取消结果
    """
    # 取消 Celery 任务
    task_result = celery_app.AsyncResult(task_id)
    task_result.revoke(terminate=True)
    
    return JSONResponse(content={
        "task_id": task_id,
        "status": "cancelled"
    })