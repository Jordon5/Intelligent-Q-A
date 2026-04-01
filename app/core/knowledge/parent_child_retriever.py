"""父子块检索工具"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class ParentChildRetriever:
    """父子块检索工具
    
    在检索阶段使用子块进行精确匹配，在生成阶段通过父块 ID 召回完整上下文
    """

    def __init__(self, knowledge_base_dir: str = "./data/knowledge"):
        """
        初始化父子块检索工具

        Args:
            knowledge_base_dir: 知识库存储目录
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)

    def get_parent_chunk(self, child_chunk: Dict[str, Any], kb_id: str) -> Optional[Dict[str, Any]]:
        """
        根据子块获取对应的父块

        Args:
            child_chunk: 子块
            kb_id: 知识库 ID

        Returns:
            对应的父块，如果不存在则返回 None
        """
        parent_id = child_chunk.get('parent_id')
        if not parent_id:
            return None

        # 读取父块信息
        parent_chunks = self._load_parent_chunks(kb_id)
        if not parent_chunks:
            return None

        # 查找对应的父块
        for parent in parent_chunks:
            if parent['id'] == parent_id:
                return parent

        return None

    def get_parent_chunks_from_children(self, child_chunks: List[Dict[str, Any]], kb_id: str) -> List[Dict[str, Any]]:
        """
        从子块列表获取对应的父块列表

        Args:
            child_chunks: 子块列表
            kb_id: 知识库 ID

        Returns:
            父块列表，去重后返回
        """
        parent_chunks = []
        parent_ids = set()

        for child in child_chunks:
            parent = self.get_parent_chunk(child, kb_id)
            if parent and parent['id'] not in parent_ids:
                parent_chunks.append(parent)
                parent_ids.add(parent['id'])

        return parent_chunks

    def _load_parent_chunks(self, kb_id: str) -> List[Dict[str, Any]]:
        """
        加载知识库的父块信息

        Args:
            kb_id: 知识库 ID

        Returns:
            父块列表
        """
        kb_dir = self.knowledge_base_dir / kb_id
        parent_chunks_path = kb_dir / "parent_chunks.json"

        if not parent_chunks_path.exists():
            return []

        try:
            with open(parent_chunks_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def enhance_retrieval_results(self, retrieval_results: List[Dict[str, Any]], kb_id: str) -> List[Dict[str, Any]]:
        """
        增强检索结果，用父块替换子块，提供完整上下文

        Args:
            retrieval_results: 检索结果（子块）
            kb_id: 知识库 ID

        Returns:
            增强后的检索结果（父块）
        """
        # 获取对应的父块
        parent_chunks = self.get_parent_chunks_from_children(retrieval_results, kb_id)

        # 按照子块的相关性排序父块
        # 这里可以根据需要实现更复杂的排序逻辑
        # 简单起见，这里直接返回父块
        return parent_chunks

    def get_combined_context(self, retrieval_results: List[Dict[str, Any]], kb_id: str, max_context_length: int = 4000) -> str:
        """
        获取组合的上下文，用于 LLM 生成

        Args:
            retrieval_results: 检索结果（子块）
            kb_id: 知识库 ID
            max_context_length: 最大上下文长度

        Returns:
            组合的上下文文本
        """
        # 获取父块
        parent_chunks = self.enhance_retrieval_results(retrieval_results, kb_id)

        # 组合上下文
        context_parts = []
        total_length = 0

        for parent in parent_chunks:
            parent_text = parent.get('text', '')
            part_length = len(parent_text)

            if total_length + part_length <= max_context_length:
                context_parts.append(parent_text)
                total_length += part_length
            else:
                # 如果超过最大长度，截断最后一个父块
                remaining_length = max_context_length - total_length
                if remaining_length > 0:
                    context_parts.append(parent_text[:remaining_length])
                break

        return '\n\n'.join(context_parts)