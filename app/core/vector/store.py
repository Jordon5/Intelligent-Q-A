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
    
    def hybrid_search(self, store_name: str, query: str, query_embedding: List[float], top_k: int = 5, method: str = 'rrf', rrf_k: int = 60, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        混合检索：BM25 + 向量检索
        
        Args:
            store_name: 向量存储名称
            query: 查询文本
            query_embedding: 查询嵌入
            top_k: 返回前 k 个结果
            method: 融合方法 ('rrf' 倒数排名融合, 'weighted' 加权融合)
            rrf_k: RRF 平滑常数，通常取 60
            alpha: 加权融合时向量检索的权重 (0-1)
            
        Returns:
            混合检索结果列表
        """
        try:
            vector_results = self.search(store_name, query_embedding, top_k * 2)
            bm25_results = self.bm25_search(store_name, query, top_k * 2)
            
            if method == 'rrf':
                return self._reciprocal_rank_fusion(vector_results, bm25_results, top_k, rrf_k)
            else:
                return self._weighted_fusion(vector_results, bm25_results, top_k, alpha)
        except Exception:
            return []
    
    def _reciprocal_rank_fusion(self, vector_results: List[Dict[str, Any]], bm25_results: List[Dict[str, Any]], top_k: int, k: int = 60) -> List[Dict[str, Any]]:
        """
        标准倒数排名融合算法 (Reciprocal Rank Fusion)
        
        RRF 公式：RRF(d) = Σ 1 / (k + rank(d))
        
        优点：不依赖原始分数分布，只依赖排名，解决了不同检索系统分数不可比的问题
        
        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            top_k: 返回前 k 个结果
            k: 平滑常数，通常取 60
            
        Returns:
            融合后的结果
        """
        scores = {}
        doc_info = {}
        
        for rank, result in enumerate(vector_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
                doc_info[doc_id] = result
            scores[doc_id] += 1.0 / (k + rank)
        
        for rank, result in enumerate(bm25_results, 1):
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
                doc_info[doc_id] = result
            scores[doc_id] += 1.0 / (k + rank)
        
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        fused_results = []
        for doc_id, score in sorted_docs:
            result = doc_info[doc_id].copy()
            result['rrf_score'] = score
            fused_results.append(result)
        
        return fused_results
    
    def _weighted_fusion(self, vector_results: List[Dict[str, Any]], bm25_results: List[Dict[str, Any]], top_k: int, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        加权融合算法 (先归一化分数，再加权)
        
        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            top_k: 返回前 k 个结果
            alpha: 向量检索权重 (0-1)，BM25 权重为 (1-alpha)
            
        Returns:
            融合后的结果
        """
        def normalize_scores(results):
            if not results:
                return results
            scores = [r['score'] for r in results]
            min_s, max_s = min(scores), max(scores)
            if max_s == min_s:
                for r in results:
                    r['normalized_score'] = 1.0
            else:
                for r in results:
                    r['normalized_score'] = (r['score'] - min_s) / (max_s - min_s)
            return results
        
        vector_results = normalize_scores(vector_results.copy())
        bm25_results = normalize_scores(bm25_results.copy())
        
        scores = {}
        doc_info = {}
        
        for result in vector_results:
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
                doc_info[doc_id] = result
            scores[doc_id] += alpha * result['normalized_score']
        
        for result in bm25_results:
            doc_id = result['id']
            if doc_id not in scores:
                scores[doc_id] = 0
                doc_info[doc_id] = result
            scores[doc_id] += (1 - alpha) * result['normalized_score']
        
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        fused_results = []
        for doc_id, score in sorted_docs:
            result = doc_info[doc_id].copy()
            result['fusion_score'] = score
            fused_results.append(result)
        
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
