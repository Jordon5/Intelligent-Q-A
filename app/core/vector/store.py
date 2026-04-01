"""向量存储管理器"""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

from chromadb import Client as ChromaClient
from chromadb.config import Settings
from rank_bm25 import BM25Okapi

class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self, persist_dir: str = "./data/vector"):
        """
        初始化向量存储管理器
        
        Args:
            persist_dir: 向量存储持久化目录
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 ChromaDB 客户端
        self.client = ChromaClient(
            settings=Settings(
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False
            )
        )
        
        # 存储 BM25 索引
        self.bm25_indexes = {}
        # 存储文档文本，用于 BM25 检索
        self.document_texts = {}
    
    def create_vector_store(self, name: str, embedding_dim: int = 1024) -> bool:
        """
        创建向量存储
        
        Args:
            name: 向量存储名称
            embedding_dim: 嵌入维度
            
        Returns:
            是否创建成功
        """
        try:
            # 检查向量存储是否已存在
            collections = self.client.list_collections()
            existing_names = [col.name for col in collections]
            
            if name not in existing_names:
                # 创建新的向量存储
                self.client.create_collection(
                    name=name,
                    metadata={"embedding_dim": embedding_dim}
                )
            return True
        except Exception:
            return False
    
    def _tokenize(self, text: str) -> List[str]:
        """
        分词函数，用于 BM25
        
        Args:
            text: 文本
            
        Returns:
            分词后的列表
        """
        # 简单的分词实现，可根据需要替换为更复杂的分词器
        # 对于中文，每个字符作为一个token
        # 对于英文，保留完整单词
        tokens = []
        
        # 处理中文
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
        tokens.extend(chinese_chars)
        
        # 处理英文
        english_words = re.findall(r'[a-zA-Z]+', text)
        tokens.extend(english_words)
        
        return tokens
    
    def add_documents(self, store_name: str, documents: List[Dict[str, Any]]) -> bool:
        """
        向向量存储添加文档
        
        Args:
            store_name: 向量存储名称
            documents: 文档列表，每个文档包含 id, text, embedding 等字段
            
        Returns:
            是否添加成功
        """
        try:
            collection = self.client.get_collection(name=store_name)
            
            # 准备数据
            ids = []
            texts = []
            embeddings = []
            metadatas = []
            
            for doc in documents:
                ids.append(doc.get("id"))
                texts.append(doc.get("text"))
                embeddings.append(doc.get("embedding"))
                metadatas.append(doc.get("metadata", {}))
            
            # 添加文档到向量存储
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            # 更新 BM25 索引
            if store_name not in self.document_texts:
                self.document_texts[store_name] = {}
            
            # 添加文档文本到存储
            for doc_id, text in zip(ids, texts):
                self.document_texts[store_name][doc_id] = text
            
            # 重建 BM25 索引
            self._build_bm25_index(store_name)
            
            return True
        except Exception:
            return False
    
    def _build_bm25_index(self, store_name: str):
        """
        构建 BM25 索引
        
        Args:
            store_name: 向量存储名称
        """
        if store_name not in self.document_texts or not self.document_texts[store_name]:
            return
        
        # 获取所有文档文本
        doc_texts = list(self.document_texts[store_name].values())
        doc_ids = list(self.document_texts[store_name].keys())
        
        # 分词
        tokenized_corpus = [self._tokenize(text) for text in doc_texts]
        
        # 创建 BM25 索引
        bm25 = BM25Okapi(tokenized_corpus)
        
        # 存储索引和文档 ID 映射
        self.bm25_indexes[store_name] = {
            'index': bm25,
            'doc_ids': doc_ids
        }
    
    def search(self, store_name: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        在向量存储中搜索
        
        Args:
            store_name: 向量存储名称
            query_embedding: 查询嵌入
            top_k: 返回前 k 个结果
            
        Returns:
            搜索结果列表
        """
        try:
            collection = self.client.get_collection(name=store_name)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # 处理结果
            search_results = []
            for i in range(len(results["ids"][0])):
                search_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "score": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
            
            return search_results
        except Exception:
            return []
    
    def bm25_search(self, store_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        使用 BM25 进行关键词检索
        
        Args:
            store_name: 向量存储名称
            query: 查询文本
            top_k: 返回前 k 个结果
            
        Returns:
            搜索结果列表
        """
        try:
            if store_name not in self.bm25_indexes:
                # 如果 BM25 索引不存在，尝试构建
                self._build_bm25_index(store_name)
                
            if store_name not in self.bm25_indexes:
                return []
            
            bm25_data = self.bm25_indexes[store_name]
            bm25 = bm25_data['index']
            doc_ids = bm25_data['doc_ids']
            
            # 分词查询
            tokenized_query = self._tokenize(query)
            
            # 获取 BM25 得分
            scores = bm25.get_scores(tokenized_query)
            
            # 排序并获取 top_k
            top_indices = scores.argsort()[::-1][:top_k]
            
            # 构建结果
            results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    doc_id = doc_ids[idx]
                    text = self.document_texts[store_name].get(doc_id, "")
                    results.append({
                        "id": doc_id,
                        "text": text,
                        "score": float(scores[idx]),
                        "metadata": {}
                    })
            
            return results
        except Exception:
            return []
    
    def hybrid_search(self, store_name: str, query: str, query_embedding: List[float], top_k: int = 5, bm25_weight: float = 0.5) -> List[Dict[str, Any]]:
        """
        混合检索：BM25 + 向量检索
        
        Args:
            store_name: 向量存储名称
            query: 查询文本
            query_embedding: 查询嵌入
            top_k: 返回前 k 个结果
            bm25_weight: BM25 权重
            
        Returns:
            混合检索结果列表
        """
        try:
            # 获取两种检索结果
            vector_results = self.search(store_name, query_embedding, top_k * 2)
            bm25_results = self.bm25_search(store_name, query, top_k * 2)
            
            # 倒数排名融合
            fused_results = self._reciprocal_rank_fusion(vector_results, bm25_results, top_k)
            
            return fused_results
        except Exception:
            return []
    
    def _reciprocal_rank_fusion(self, vector_results: List[Dict[str, Any]], bm25_results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """
        倒数排名融合算法
        
        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            top_k: 返回前 k 个结果
            
        Returns:
            融合后的结果
        """
        # 计算每个文档的倒数排名得分
        scores = {}
        
        # 处理向量检索结果
        for rank, result in enumerate(vector_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
            # 向量检索使用距离，需要转换为相似度
            distance = result.get('score', 0)
            similarity = 1.0 / (1.0 + distance)  # 转换为相似度
            scores[doc_id] += similarity / rank
        
        # 处理 BM25 结果
        for rank, result in enumerate(bm25_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
            bm25_score = result.get('score', 0)
            # 归一化 BM25 得分
            normalized_score = bm25_score / (bm25_score + 1) if bm25_score > 0 else 0
            scores[doc_id] += normalized_score / rank
        
        # 排序并获取 top_k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # 构建最终结果
        fused_results = []
        for doc_id, score in sorted_docs:
            # 从原始结果中获取文档信息
            doc_info = None
            for result in vector_results:
                if result['id'] == doc_id:
                    doc_info = result
                    break
            if not doc_info:
                for result in bm25_results:
                    if result['id'] == doc_id:
                        doc_info = result
                        break
            
            if doc_info:
                fused_result = doc_info.copy()
                fused_result['score'] = score
                fused_results.append(fused_result)
        
        return fused_results
    
    def delete_vector_store(self, name: str) -> bool:
        """
        删除向量存储
        
        Args:
            name: 向量存储名称
            
        Returns:
            是否删除成功
        """
        try:
            # 删除 ChromaDB 集合
            self.client.delete_collection(name=name)
            
            # 删除 BM25 索引
            if name in self.bm25_indexes:
                del self.bm25_indexes[name]
            
            # 删除文档文本
            if name in self.document_texts:
                del self.document_texts[name]
            
            return True
        except Exception:
            return False
    
    def list_vector_stores(self) -> List[str]:
        """
        列出所有向量存储
        
        Returns:
            向量存储名称列表
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception:
            return []
    
    def get_vector_store_stats(self, name: str) -> Dict[str, Any]:
        """
        获取向量存储统计信息
        
        Args:
            name: 向量存储名称
            
        Returns:
            统计信息
        """
        try:
            collection = self.client.get_collection(name=name)
            count = collection.count()
            return {
                "name": name,
                "document_count": count
            }
        except Exception:
            return {
                "name": name,
                "document_count": 0
            }
