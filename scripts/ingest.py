#!/usr/bin/env python3
"""
数据摄入脚本 - 将知识文件导入向量数据库
"""
import asyncio
import sys
import os
import uuid
from pathlib import Path
import logging

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.llm import create_qwen_provider
from src.vector_store import create_chroma_vector_store, VectorDocument
from src.utils.markdown import read_markdown_file
from src.utils.chunking import TextChunker


class Ingestor:
    """数据摄入器"""
    
    def __init__(self):
        """初始化摄入器"""
        self.settings = get_settings()
        self.llm_provider = None
        self.vector_store = None
        self.chunker = TextChunker(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.logger = logging.getLogger(__name__)
    
    async def init(self):
        """初始化组件"""
        # 检查 API 密钥
        if not self.settings.qwen_api_key:
            self.logger.error("QWEN_API_KEY 未配置")
            sys.exit(1)
        
        # 初始化 LLM 提供商
        self.llm_provider = create_qwen_provider(
            api_key=self.settings.qwen_api_key,
            chat_model=self.settings.qwen_chat_model,
            embed_model=self.settings.qwen_embed_model,
            base_url=self.settings.qwen_chat_base,
            embed_dim=self.settings.embed_dim,
        )
        
        # 初始化向量存储
        self.vector_store = create_chroma_vector_store(
            persist_dir=self.settings.chroma_persist_dir,
            collection_name=self.settings.chroma_collection_name,
            embedding_dim=self.settings.embed_dim,
        )
    
    async def close(self):
        """关闭资源"""
        if self.llm_provider:
            await self.llm_provider.close()
    
    async def process_file(self, file_path: Path) -> int:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理的块数
        """
        try:
            self.logger.info(f"处理文件: {file_path}")
            
            # 读取 Markdown 文件
            text, metadata = read_markdown_file(file_path)
            
            # 提取类别（从目录结构）
            category = file_path.parent.name
            
            # 增强元数据
            metadata.update({
                "source": str(file_path.relative_to(self.settings.character_dir)),
                "category": category,
                "character": self.settings.character_name,
                "era": self.settings.character_era,
            })
            
            # 文本分块
            chunks = self.chunker.chunk(text, metadata=metadata)
            self.logger.info(f"文件分块: {len(chunks)} 块")
            
            if not chunks:
                return 0
            
            # 批量生成嵌入
            batch_size = 10
            total_chunks = len(chunks)
            processed_chunks = 0
            
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i+batch_size]
                texts = [chunk['text'] for chunk in batch]
                
                # 生成嵌入
                embed_response = await self.llm_provider.embed(texts)
                
                # 构建文档
                documents = []
                for j, (chunk, embedding) in enumerate(zip(batch, embed_response.embeddings)):
                    doc_id = str(uuid.uuid4())
                    document = VectorDocument(
                        id=doc_id,
                        text=chunk['text'],
                        vector=embedding,
                        metadata=chunk['metadata'],
                    )
                    documents.append(document)
                
                # 添加到向量存储
                await self.vector_store.add_documents(documents)
                processed_chunks += len(documents)
                self.logger.info(f"处理进度: {processed_chunks}/{total_chunks} 块")
            
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"处理文件失败 {file_path}: {e}", exc_info=True)
            return 0
    
    async def process_directory(self, directory: Path) -> int:
        """
        处理目录
        
        Args:
            directory: 目录路径
            
        Returns:
            处理的文件数
        """
        if not directory.exists():
            self.logger.warning(f"目录不存在: {directory}")
            return 0
        
        markdown_files = list(directory.rglob("*.md"))
        self.logger.info(f"找到 {len(markdown_files)} 个 Markdown 文件")
        
        total_files = 0
        total_chunks = 0
        
        for file_path in markdown_files:
            chunks_processed = await self.process_file(file_path)
            if chunks_processed > 0:
                total_files += 1
                total_chunks += chunks_processed
        
        return total_files, total_chunks
    
    async def run(self):
        """运行摄入流程"""
        try:
            await self.init()
            
            # 清空现有数据
            self.logger.info("清空向量存储...")
            await self.vector_store.clear_all()
            
            # 处理知识目录
            self.logger.info(f"开始处理知识目录: {self.settings.character_dir}")
            total_files, total_chunks = await self.process_directory(self.settings.character_dir)
            
            # 统计信息
            self.logger.info(f"摄入完成:")
            self.logger.info(f"  处理文件数: {total_files}")
            self.logger.info(f"  处理块数: {total_chunks}")
            self.logger.info(f"  向量库文档数: {await self.vector_store.count()}")
            
        except KeyboardInterrupt:
            self.logger.info("摄入被用户中断")
        except Exception as e:
            self.logger.error(f"致命错误: {e}", exc_info=True)
            sys.exit(1)
        finally:
            await self.close()


def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    ingestor = Ingestor()
    asyncio.run(ingestor.run())


if __name__ == "__main__":
    main()