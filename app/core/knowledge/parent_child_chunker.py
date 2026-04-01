"""父子索引分块工具"""

from typing import List, Dict, Any, Tuple
import hashlib

class ParentChildChunker:
    """父子索引分块器
    
    在索引阶段使用小区块保证检索精度，在生成阶段通过ID关联召回父级大区块
    """

    def __init__(
            self,
            parent_chunk_size: int = 2000,
            child_chunk_size: int = 600,
            child_chunk_overlap: int = 50,
            separators: List[str] = None
            ):
        """
        初始化父子分块器

        Args:
            parent_chunk_size: 父块大小
            child_chunk_size: 子块大小
            child_chunk_overlap: 子块重叠大小
            separators: 分隔符列表
        """
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap
        self.separators = separators or [
            '\n\n',  # 段落
            '\n',    # 行
            '。', '！', '？', '.', '!', '?',  # 句子
            '，', ',',  # 逗号
        ]

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        对文本进行父子分块

        Args:
            text: 输入文本
            metadata: 元数据字典

        Returns:
            (父块列表, 子块列表)
        """
        # 1. 首先生成父块
        parent_chunks = self._create_parent_chunks(text, metadata)
        
        # 2. 为每个父块生成子块
        child_chunks = []
        for parent_chunk in parent_chunks:
            parent_id = parent_chunk['id']
            childs = self._create_child_chunks(parent_chunk['text'], parent_id, parent_chunk['metadata'])
            child_chunks.extend(childs)
        
        return parent_chunks, child_chunks
    
    def _create_parent_chunks(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        创建父块
        """
        chunks = []
        current_chunk = []
        current_length = 0

        parts = self._split_by_separators(text)

        for part in parts:
            part_length = len(part)
            if current_length + part_length <= self.parent_chunk_size:
                current_chunk.append(part)
                current_length += part_length
            else:
                if current_chunk:
                    chunk_text = ''.join(current_chunk)
                    chunk_id = self._generate_chunk_id(chunk_text)
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": metadata.copy() if metadata else {},
                        "length": len(chunk_text),
                        "type": "parent"
                    })
                
                # 开始新的父块
                current_chunk = [part]
                current_length = part_length

        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunk_id = self._generate_chunk_id(chunk_text)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'metadata': metadata.copy() if metadata else {},
                'length': len(chunk_text),
                'type': 'parent'
            })
        
        for i, chunk in enumerate(chunks):
            chunk['metadata']['parent_index'] = i
            chunk['metadata']['total_parents'] = len(chunks)
        
        return chunks
    
    def _create_child_chunks(self, parent_text: str, parent_id: str, parent_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为父块创建子块
        """
        chunks = []
        current_chunk = []
        current_length = 0

        parts = self._split_by_separators(parent_text)

        for part in parts:
            part_length = len(part)
            if current_length + part_length <= self.child_chunk_size:
                current_chunk.append(part)
                current_length += part_length
            else:
                if current_chunk:
                    chunk_text = ''.join(current_chunk)
                    chunk_id = self._generate_chunk_id(chunk_text)
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": parent_metadata.copy(),
                        "length": len(chunk_text),
                        "type": "child",
                        "parent_id": parent_id
                    })
                
                overlap = ''.join(current_chunk[-self.child_chunk_overlap//10:]) if current_chunk else ''
                current_chunk = [overlap, part]
                current_length = len(overlap) + part_length

        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunk_id = self._generate_chunk_id(chunk_text)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'metadata': parent_metadata.copy(),
                'length': len(chunk_text),
                'type': 'child',
                'parent_id': parent_id
            })
        
        for i, chunk in enumerate(chunks):
            chunk['metadata']['child_index'] = i
            chunk['metadata']['total_children'] = len(chunks)
        
        return chunks
    
    def _split_by_separators(self, text: str) -> List[str]:
        """ 对文本进行分隔符分隔 """
        parts = [text]

        for sep in self.separators:
            new_parts = []
            for part in parts:
                subparts = part.split(sep)
                for i, subpart in enumerate(subparts):
                    if subpart:
                        new_parts.append(subpart)
                    if i < len(subparts) - 1:
                        new_parts.append(sep)
            parts = new_parts

        return parts
    
    def _generate_chunk_id(self, text: str) -> str:
        """
        生成块的唯一ID
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_parent_chunk(self, child_chunk: Dict[str, Any], parent_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据子块获取对应的父块
        
        Args:
            child_chunk: 子块
            parent_chunks: 父块列表
            
        Returns:
            对应的父块
        """
        parent_id = child_chunk.get('parent_id')
        if not parent_id:
            return None
        
        for parent in parent_chunks:
            if parent['id'] == parent_id:
                return parent
        
        return None