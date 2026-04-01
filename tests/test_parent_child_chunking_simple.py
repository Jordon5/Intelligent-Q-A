"""独立测试父子分块功能"""
import hashlib
from typing import List, Dict, Any, Tuple

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


def test_parent_child_chunking():
    """测试父子分块功能"""
    print("=== 父子索引分块策略测试 ===\n")
    
    # 创建测试文本
    test_text = """陈平安是齐静春代替文圣收的徒弟，齐静春为其传道。齐静春是山崖书院的山主，负责教导学生。陈平安的师傅是文圣，齐静春是他的引路人。

齐静春说话的语气偏教书先生的语气，不用那么苍老。他是一位学识渊博的学者，对陈平安的成长起到了重要的作用。

陈平安在齐静春的指导下，逐渐成长为一名有担当的年轻人。齐静春虽然去世了，但他的教导一直影响着陈平安。

在故事的发展中，陈平安经历了许多困难和挑战，但他始终记得齐静春的教诲，坚持自己的信念。

齐静春的精神和教导成为陈平安前进的动力，帮助他度过了许多难关。"""
    
    # 初始化父子分块器
    chunker = ParentChildChunker(
        parent_chunk_size=800,
        child_chunk_size=300,
        child_chunk_overlap=50
    )
    
    # 生成父子块
    print("[INFO] 生成父子块...")
    parent_chunks, child_chunks = chunker.chunk(test_text, metadata={"source": "test"})
    
    print(f"[OK] 生成完成")
    print(f"- 父块数量: {len(parent_chunks)}")
    print(f"- 子块数量: {len(child_chunks)}")
    
    # 显示父块
    print("\n1. 父块内容:")
    for i, parent in enumerate(parent_chunks):
        print(f"\n父块 {i+1} (长度: {parent['length']}):")
        print("-" * 50)
        print(parent['text'])
        print("-" * 50)
    
    # 显示子块
    print("\n2. 子块内容:")
    for i, child in enumerate(child_chunks):
        print(f"\n子块 {i+1} (长度: {child['length']}, 父块ID: {child['parent_id'][:8]}...):")
        print("-" * 50)
        print(child['text'])
        print("-" * 50)
    
    # 测试父子关联
    print("\n3. 测试父子关联:")
    if child_chunks:
        test_child = child_chunks[0]
        parent = chunker.get_parent_chunk(test_child, parent_chunks)
        if parent:
            print(f"子块 1 对应的父块:")
            print(f"- 父块ID: {parent['id'][:8]}...")
            print(f"- 父块内容:")
            print(parent['text'])
        else:
            print("无法找到对应的父块")
    
    # 测试检索增强
    print("\n4. 测试检索增强:")
    # 模拟检索结果（子块）
    mock_retrieval_results = child_chunks[:2]  # 假设前两个子块是检索结果
    
    print("模拟检索结果（子块）:")
    for i, child in enumerate(mock_retrieval_results):
        print(f"\n检索结果 {i+1}:")
        print(child['text'])
    
    # 增强检索结果
    enhanced_results = []
    for child in mock_retrieval_results:
        parent = chunker.get_parent_chunk(child, parent_chunks)
        if parent and parent not in enhanced_results:
            enhanced_results.append(parent)
    
    print("\n增强后的检索结果（父块）:")
    for i, parent in enumerate(enhanced_results):
        print(f"\n增强结果 {i+1}:")
        print(parent['text'])
    
    # 测试上下文组合
    print("\n5. 测试上下文组合:")
    combined_context = '\n\n'.join([p['text'] for p in enhanced_results])
    print(f"组合上下文长度: {len(combined_context)}")
    print("组合上下文:")
    print("-" * 50)
    print(combined_context)
    print("-" * 50)
    
    print("\n[OK] 测试完成")


if __name__ == "__main__":
    print("开始父子索引分块策略测试...\n")
    test_parent_child_chunking()
    print("\n=== 测试完成 ===")
    print("父子索引分块策略已成功实现：")
    print("- 小区块保证检索精度")
    print("- 大区块提供完整上下文")
    print("- ID 关联实现父子映射")
    print("- 有效提升 LLM 回答连贯性")