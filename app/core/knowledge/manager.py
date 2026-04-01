"""知识库管理器"""
import os
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from .parser import DocumentParser
from .parent_child_chunker import ParentChildChunker
from ..vector.store import VectorStoreManager


@dataclass
class KnowledgeBase:
    """知识库类"""
    id: str
    name: str
    description: str
    version: str
    created_at: str
    author: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    documents: List[str]
    vector_store_name: Optional[str] = None


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, knowledge_base_dir: str = "./data/knowledge"):
        """
        初始化知识库管理器
        
        Args:
            knowledge_base_dir: 知识库存储目录
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.parser = DocumentParser()
        self.vector_store_manager = VectorStoreManager()
    
    def validate_knowledge_base(self, kb_path: str) -> Dict[str, Any]:
        """
        验证知识库格式
        
        Args:
            kb_path: 知识库路径
            
        Returns:
            验证结果，包含是否有效和错误信息
        """
        kb_path = Path(kb_path)
        
        # 检查目录是否存在
        if not kb_path.exists() or not kb_path.is_dir():
            return {
                "valid": False,
                "error": f"知识库目录不存在: {kb_path}"
            }
        
        # 检查 metadata.json 文件
        metadata_path = kb_path / "metadata.json"
        if not metadata_path.exists():
            return {
                "valid": False,
                "error": "缺少 metadata.json 文件"
            }
        
        # 检查 documents 目录
        documents_path = kb_path / "documents"
        if not documents_path.exists() or not documents_path.is_dir():
            return {
                "valid": False,
                "error": "缺少 documents 目录"
            }
        
        # 检查是否有文档文件
        document_files = list(documents_path.glob("*"))
        if not document_files:
            return {
                "valid": False,
                "error": "documents 目录为空"
            }
        
        # 验证 metadata.json 格式
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 检查必要字段
            required_fields = ["name", "description", "version", "created_at", "author"]
            for field in required_fields:
                if field not in metadata:
                    return {
                        "valid": False,
                        "error": f"metadata.json 缺少必要字段: {field}"
                    }
            
            # 检查可选字段
            if "embedding_model" not in metadata:
                metadata["embedding_model"] = "text-embedding-v4"
            if "chunk_size" not in metadata:
                metadata["chunk_size"] = 1000
            if "chunk_overlap" not in metadata:
                metadata["chunk_overlap"] = 200
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"metadata.json 格式错误: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"验证 metadata.json 时出错: {str(e)}"
            }
        
        # 验证文档文件格式
        valid_extensions = [".md", ".pdf", ".txt", ".docx", ".json"]
        for doc_file in document_files:
            if doc_file.suffix.lower() not in valid_extensions:
                return {
                    "valid": False,
                    "error": f"不支持的文件格式: {doc_file.name}"
                }
        
        return {
            "valid": True,
            "metadata": metadata,
            "documents": [str(f.relative_to(kb_path)) for f in document_files]
        }
    
    def process_knowledge_base(self, kb_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识库并生成向量存储
        
        Args:
            kb_path: 知识库路径
            config: 处理配置
            
        Returns:
            处理结果，包含知识库信息和向量存储名称
        """
        # 验证知识库
        validation_result = self.validate_knowledge_base(kb_path)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        kb_path = Path(kb_path)
        metadata = validation_result["metadata"]
        documents = validation_result["documents"]
        
        # 生成知识库 ID
        import uuid
        kb_id = str(uuid.uuid4())[:8]
        
        # 创建知识库目录
        kb_dir = self.knowledge_base_dir / kb_id
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制知识库文件
        try:
            # 复制 metadata.json
            shutil.copy(kb_path / "metadata.json", kb_dir / "metadata.json")
            
            # 复制 documents 目录
            dest_documents_dir = kb_dir / "documents"
            dest_documents_dir.mkdir(parents=True, exist_ok=True)
            for doc_file in Path(kb_path / "documents").glob("*"):
                shutil.copy(doc_file, dest_documents_dir / doc_file.name)
        except Exception as e:
            return {
                "success": False,
                "error": f"复制知识库文件时出错: {str(e)}"
            }
        
        # 解析文档
        parsed_documents = []
        documents_path = kb_dir / "documents"
        for doc_file in documents_path.glob("*"):
            try:
                content = self.parser.parse(str(doc_file))
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
        parent_chunks_store = f"kb_{kb_id}_parents"
        
        try:
            # 初始化父子分块器
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
                self.vector_store_manager.create_vector_store(vector_store_name)
                
                # 准备子块数据
                child_documents = []
                for child in all_child_chunks:
                    # 生成嵌入（使用临时占位符，实际应用中应该使用真实的嵌入生成）
                    embedding = self._generate_temp_embedding(child["text"])
                    child_documents.append({
                        "id": child["id"],
                        "text": child["text"],
                        "embedding": embedding,
                        "metadata": child["metadata"]
                    })
                
                # 添加到向量存储
                self.vector_store_manager.add_documents(vector_store_name, child_documents)
            
            # 保存父块信息
            if all_parent_chunks:
                parent_chunks_path = kb_dir / "parent_chunks.json"
                with open(parent_chunks_path, "w", encoding="utf-8") as f:
                    json.dump(all_parent_chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return {
                "success": False,
                "error": f"生成向量存储时出错: {str(e)}"
            }
        
        # 创建知识库对象
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
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        列出所有知识库
        
        Returns:
            知识库列表
        """
        knowledge_bases = []
        
        for kb_dir in self.knowledge_base_dir.glob("*"):
            if kb_dir.is_dir():
                kb_info_path = kb_dir / "kb_info.json"
                if kb_info_path.exists():
                    try:
                        with open(kb_info_path, "r", encoding="utf-8") as f:
                            kb_info = json.load(f)
                        knowledge_bases.append(kb_info)
                    except Exception:
                        pass
        
        return knowledge_bases
    
    def get_knowledge_base(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """
        获取知识库信息
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            知识库信息，如果不存在则返回 None
        """
        kb_dir = self.knowledge_base_dir / kb_id
        kb_info_path = kb_dir / "kb_info.json"
        
        if kb_info_path.exists():
            try:
                with open(kb_info_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            是否删除成功
        """
        kb_dir = self.knowledge_base_dir / kb_id
        
        if kb_dir.exists() and kb_dir.is_dir():
            try:
                # 删除向量存储
                kb_info_path = kb_dir / "kb_info.json"
                if kb_info_path.exists():
                    try:
                        with open(kb_info_path, "r", encoding="utf-8") as f:
                            kb_info = json.load(f)
                        if "vector_store_name" in kb_info:
                            # 这里需要调用向量存储管理器来删除向量存储
                            pass
                    except Exception:
                        pass
                
                # 删除知识库目录
                shutil.rmtree(kb_dir)
                return True
            except Exception:
                pass
        
        return False
    
    def _generate_temp_embedding(self, text: str) -> List[float]:
        """
        生成临时嵌入（用于测试）
        
        在实际应用中，应该使用真实的嵌入生成服务
        这里使用简单的哈希方法生成临时嵌入
        
        Args:
            text: 文本
            
        Returns:
            嵌入向量
        """
        import hashlib
        import numpy as np
        
        # 使用文本哈希生成伪随机嵌入
        hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 将哈希值转换为1024维向量
        embedding = []
        for i in range(0, len(hash_value), 2):
            if i + 1 < len(hash_value):
                value = int(hash_value[i:i+2], 16) / 255.0 - 0.5
            else:
                value = int(hash_value[i], 16) / 255.0 - 0.5
            embedding.append(value)
        
        # 补齐到1024维
        while len(embedding) < 1024:
            embedding.append(0.0)
        
        # 截断到1024维
        embedding = embedding[:1024]
        
        return embedding
