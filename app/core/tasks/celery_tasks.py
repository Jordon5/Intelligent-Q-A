"""Celery 任务定义"""
from celery import Task
from typing import Dict, Any
import logging
from pathlib import Path
import json
import hashlib
import tempfile
import shutil

from .celery_config import celery_app
from ..knowledge.manager import KnowledgeBaseManager


logger = logging.getLogger(__name__)


class KnowledgeBaseProcessingTask(Task):
    """知识库处理任务"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kb_manager = None
    
    def __call__(self, *args, **kwargs):
        """任务执行"""
        try:
            # 初始化知识库管理器
            self.kb_manager = KnowledgeBaseManager()
            
            # 执行处理
            result = self.process_knowledge_base(*args, **kwargs)
            
            return result
        except Exception as e:
            logger.error(f"Knowledge base processing failed: {e}", exc_info=True)
            raise
    
    def process_knowledge_base(self, kb_path: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理知识库
        
        Args:
            kb_path: 知识库路径
            config: 处理配置
            
        Returns:
            处理结果
        """
        try:
            # 验证知识库
            validation_result = self.kb_manager.validate_knowledge_base(kb_path)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            kb_path = Path(kb_path)
            metadata = validation_result["metadata"]
            
            # 生成知识库 ID
            import uuid
            kb_id = str(uuid.uuid4())[:8]
            
            # 创建知识库目录
            kb_dir = self.kb_manager.knowledge_base_dir / kb_id
            kb_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制知识库文件
            shutil.copy(kb_path / "metadata.json", kb_dir / "metadata.json")
            
            dest_documents_dir = kb_dir / "documents"
            dest_documents_dir.mkdir(parents=True, exist_ok=True)
            for doc_file in Path(kb_path / "documents").glob("*"):
                shutil.copy(doc_file, dest_documents_dir / doc_file.name)
            
            # 解析文档
            parsed_documents = []
            documents_path = kb_dir / "documents"
            for doc_file in documents_path.glob("*"):
                try:
                    content = self.kb_manager.parser.parse(str(doc_file))
                    parsed_documents.append({
                        "id": str(uuid.uuid4()),
                        "file_name": doc_file.name,
                        "content": content
                    })
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"解析文档 {doc_file.name} 时出错: {str(e)}"
                    }
            
            # 生成向量存储
            vector_store_name = f"kb_{kb_id}"
            
            # 初始化父子分块器
            from ..knowledge.parent_child_chunker import ParentChildChunker
            chunker = ParentChildChunker(
                parent_chunk_size=2000,
                child_chunk_size=600,
                child_chunk_overlap=50
            )
            
            # 处理所有文档
            all_parent_chunks = []
            all_child_chunks = []
            
            for doc in parsed_documents:
                # 生成父子块
                parent_chunks, child_chunks = chunker.chunk(
                    doc["content"],
                    metadata={
                        "document_id": doc["id"],
                        "file_name": doc["file_name"]
                    }
                )
                
                all_parent_chunks.extend(parent_chunks)
                all_child_chunks.extend(child_chunks)
            
            # 为子块生成嵌入并添加到向量存储
            if all_child_chunks:
                # 创建向量存储
                self.kb_manager.vector_store_manager.create_vector_store(vector_store_name)
                
                # 准备子块数据
                child_documents = []
                for child in all_child_chunks:
                    # 生成嵌入
                    embedding = self.kb_manager._generate_temp_embedding(child["text"])
                    child_documents.append({
                        "id": child["id"],
                        "text": child["text"],
                        "embedding": embedding,
                        "metadata": child["metadata"]
                    })
                
                # 添加到向量存储
                self.kb_manager.vector_store_manager.add_documents(vector_store_name, child_documents)
            
            # 保存父块信息
            if all_parent_chunks:
                parent_chunks_path = kb_dir / "parent_chunks.json"
                with open(parent_chunks_path, "w", encoding="utf-8") as f:
                    json.dump(all_parent_chunks, f, ensure_ascii=False, indent=2)
            
            # 创建知识库对象
            from ..knowledge.manager import KnowledgeBase
            knowledge_base = KnowledgeBase(
                id=kb_id,
                name=metadata["name"],
                description=metadata["description"],
                version=metadata["version"],
                created_at=metadata["created_at"],
                author=metadata["author"],
                embedding_model=metadata.get("embedding_model", "text-embedding-v4"),
                chunk_size=metadata.get("chunk_size", 1000),
                chunk_overlap=metadata.get("chunk_overlap", 200),
                documents=[str(f.name) for f in documents_path.glob("*")],
                vector_store_name=vector_store_name
            )
            
            # 保存知识库信息
            kb_info_path = kb_dir / "kb_info.json"
            with open(kb_info_path, "w", encoding="utf-8") as f:
                json.dump(knowledge_base.__dict__, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "knowledge_base": knowledge_base.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error processing knowledge base: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"处理知识库时出错: {str(e)}"
            }


# 注册 Celery 任务
@celery_app.task(bind=True, base=KnowledgeBaseProcessingTask, name='app.core.tasks.celery_tasks.process_knowledge_base')
def process_knowledge_base_task(self, kb_path: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    处理知识库的 Celery 任务
    
    Args:
        self: 任务实例
        kb_path: 知识库路径
        config: 处理配置
        
    Returns:
        处理结果
    """
    return self.process_knowledge_base(kb_path, config)