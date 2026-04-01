"""任务调度器"""
import os
import json
import threading
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    """任务类型"""
    KNOWLEDGE_BASE_PROCESSING = "knowledge_base_processing"
    MODEL_TRAINING = "model_training"
    DATA_EXPORT = "data_export"
    OTHER = "other"


@dataclass
class Task:
    """任务类"""
    id: str
    type: TaskType
    params: Dict[str, Any]
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, task_dir: str = "./data/tasks"):
        """
        初始化任务调度器
        
        Args:
            task_dir: 任务存储目录
        """
        self.task_dir = Path(task_dir)
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self._load_tasks()
    
    def _load_tasks(self):
        """加载任务"""
        for task_file in self.task_dir.glob("*.json"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                task = Task(
                    id=task_data["id"],
                    type=TaskType(task_data["type"]),
                    params=task_data["params"],
                    status=TaskStatus(task_data["status"]),
                    created_at=task_data["created_at"],
                    started_at=task_data.get("started_at"),
                    completed_at=task_data.get("completed_at"),
                    result=task_data.get("result"),
                    error=task_data.get("error")
                )
                self.tasks[task.id] = task
            except Exception:
                pass
    
    def _save_task(self, task: Task):
        """保存任务"""
        task_file = self.task_dir / f"{task.id}.json"
        task_data = {
            "id": task.id,
            "type": task.type.value,
            "params": task.params,
            "status": task.status.value,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error
        }
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    def create_task(self, task_type: TaskType, params: Dict[str, Any]) -> str:
        """
        创建任务
        
        Args:
            task_type: 任务类型
            params: 任务参数
            
        Returns:
            任务 ID
        """
        import uuid
        import datetime
        
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=task_type,
            params=params,
            status=TaskStatus.PENDING,
            created_at=datetime.datetime.now().isoformat()
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self._save_task(task)
        
        # 启动任务
        threading.Thread(target=self._execute_task, args=(task_id,), daemon=True).start()
        
        return task_id
    
    def _execute_task(self, task_id: str):
        """
        执行任务
        
        Args:
            task_id: 任务 ID
        """
        import datetime
        
        with self.lock:
            if task_id not in self.tasks:
                return
            task = self.tasks[task_id]
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.datetime.now().isoformat()
            self._save_task(task)
        
        try:
            # 根据任务类型执行不同的操作
            if task.type == TaskType.KNOWLEDGE_BASE_PROCESSING:
                result = self._process_knowledge_base(task.params)
            elif task.type == TaskType.MODEL_TRAINING:
                result = self._train_model(task.params)
            elif task.type == TaskType.DATA_EXPORT:
                result = self._export_data(task.params)
            else:
                result = {"success": True, "message": "Task completed"}
            
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.datetime.now().isoformat()
                task.result = result
                self._save_task(task)
        except Exception as e:
            with self.lock:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.datetime.now().isoformat()
                task.error = str(e)
                self._save_task(task)
    
    def _process_knowledge_base(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识库
        
        Args:
            params: 任务参数
            
        Returns:
            处理结果
        """
        from ..knowledge.manager import KnowledgeBaseManager
        
        kb_path = params.get("kb_path")
        config = params.get("config", {})
        
        if not kb_path:
            return {"success": False, "error": "Missing kb_path parameter"}
        
        kb_manager = KnowledgeBaseManager()
        result = kb_manager.process_knowledge_base(kb_path, config)
        
        return result
    
    def _train_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        训练模型
        
        Args:
            params: 任务参数
            
        Returns:
            训练结果
        """
        # 这里实现模型训练逻辑
        # 暂时返回成功
        return {"success": True, "message": "Model training completed"}
    
    def _export_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        导出数据
        
        Args:
            params: 任务参数
            
        Returns:
            导出结果
        """
        # 这里实现数据导出逻辑
        # 暂时返回成功
        return {"success": True, "message": "Data export completed"}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态
        """
        with self.lock:
            if task_id not in self.tasks:
                return {
                    "found": False,
                    "error": "Task not found"
                }
            task = self.tasks[task_id]
            return {
                "found": True,
                "task": {
                    "id": task.id,
                    "type": task.type.value,
                    "status": task.status.value,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "result": task.result,
                    "error": task.error
                }
            }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否取消成功
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            task = self.tasks[task_id]
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return False
            # 这里可以添加实际的任务取消逻辑
            # 暂时只是更新状态
            task.status = TaskStatus.FAILED
            task.error = "Task cancelled"
            self._save_task(task)
            return True
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            status: 任务状态，None 表示所有状态
            
        Returns:
            任务列表
        """
        tasks = []
        with self.lock:
            for task in self.tasks.values():
                if status is None or task.status == status:
                    tasks.append({
                        "id": task.id,
                        "type": task.type.value,
                        "status": task.status.value,
                        "created_at": task.created_at,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "result": task.result,
                        "error": task.error
                    })
        
        # 按创建时间排序
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tasks
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否删除成功
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            del self.tasks[task_id]
            task_file = self.task_dir / f"{task_id}.json"
            if task_file.exists():
                try:
                    task_file.unlink()
                except Exception:
                    pass
            return True
