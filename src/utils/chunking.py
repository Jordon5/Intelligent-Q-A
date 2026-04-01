"""文本分块工具"""

from typing import List, Dict, Any

class TextChunker:
    """文本分块器"""

    def __init__(
            self,
            chunk_size: int = 600,
            chunk_overlap: int = 50,
            separators: List[str] = None
            ):
        """
        初始化文本分块器

        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            separators: 分隔符列表
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            '\n\n',  # 段落
            '\n',    # 行
            '。', '！', '？', '.', '!', '?',  # 句子
            '，', ',',  # 逗号
        ]

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        对文本进行分块

        Args:
            text: 输入文本
            metadata: 元数据字典

        Returns:
            块列表，每个块是一个字典，包含文本和元数据
        """
        chunks = []
        current_chunk = []
        current_length = 0

        parts = self._split_by_separators(text)

        for part in parts:
            part_length = len(part)
            if current_length + part_length <= self.chunk_size:
                current_chunk.append(part)
                current_length += part_length
            else:
                if current_chunk:
                    chunk_text = ''.join(current_chunk)
                    chunks.append({
                        "text": chunk_text,
                        "metadata": metadata.copy() if metadata else {},
                        "length": len(chunk_text),
                    })
                
                overlap = ''.join(current_chunk[-self.chunk_overlap//10:]) if current_chunk else ''
                current_chunk = [overlap, part]
                current_length = len(overlap) + part_length

        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': metadata.copy() if metadata else {},
                'length': len(chunk_text),
            })

        for i, chunk in enumerate(chunks):
            chunk['metadata']['chunk_index'] = i
            chunk['metadata']['total_chunks'] = len(chunks)
        
        return chunks
    
    def _split_by_separators(self, text: str) -> List[str]:
        """ 对文本进行分隔符分隔 """
        parts = [text]

        for sep in self.separators:
            new_parts = []
            for part in parts:
                subparts = part.split(sep)
                for i, subpart in enumerate(subparts):
                    if subparts:
                        new_parts.append(subpart)
                    if i < len(subparts) - 1:
                        new_parts.append(sep)
            parts = new_parts

        return parts


