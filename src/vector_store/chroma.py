"""Chroma向量存储"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import BaseVectorStore, VectorDocument, SearchResult

class ChromaVectorStore(BaseVectorStore):

    def __init__(
            self,
            persist_dir: str,
            collection_name: str,
            embedding_dim: int = 1024,
            ):
        super().__init__()
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.client = None
        self.collection = None

    async def _init_client(self):
        """初始化Chroma客户端"""
        if self.client is None:
           self.client = chromadb.PersistentClient(
               path=str(self.persist_dir),
               settings=Settings(
                   chromadb_db_path="duckdb+parquet",
                   persist_directory=str(self.persist_dir),
               )
           )
           self.collection = self.client.get_or_create_collection(
               name=self.collection_name,
               metadata={"hnsw:space": "cosine"}
           )

    async def add_documents(self, documents: List[VectorDocument]):
        """添加文档"""
        await self._init_client()

        ids = [doc.id for doc in documents]
        texts = [doc.text for doc in documents]
        embeddings = [doc.vector for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    async def search(self, query_vector: List[float], top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """搜索文档"""
        await self._init_client()
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=filter_metadata,
        )
        search_results = []
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            text = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            score = 1 - distance
            document = VectorDocument(
                id=doc_id,
                text=text,
                vector=query_vector,
                metadata=metadata,
            )
            search_results.append(
                SearchResult(
                    documents=document,
                    score=score,
                )
            )
        return search_results
    
    async def delete_documents(self, ids: List[str]):
        """删除文档"""
        await self._init_client()
        self.collection.delete(
            ids=ids,
        )

    async def clear_all(self):
        """清除所有文档"""
        await self._init_client()
        self.client.delete_collection(
            name=self.collection_name,
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def count(self):
        await self._init_client()
        return self.collection.count()
    
def create_chroma_vector_store(
        persist_dir: Path,
        collection_name: str = "character_knowledge",
        embedding_dim: int = 1024,
        ) -> BaseVectorStore:
    """创建Chroma向量存储"""
    return ChromaVectorStore(
        persist_dir=persist_dir,
        collection_name=collection_name,
        embedding_dim=embedding_dim,
    )

