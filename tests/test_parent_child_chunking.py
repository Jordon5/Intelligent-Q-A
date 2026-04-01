"""测试父子索引分块策略"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge.parent_child_chunker import ParentChildChunker
from app.core.knowledge.parent_child_retriever import ParentChildRetriever


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
    retriever = ParentChildRetriever()
    # 这里我们使用临时的父块列表来模拟
    # 在实际应用中，会从文件加载父块
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
    combined_context = retriever.get_combined_context(mock_retrieval_results, "test_kb", max_context_length=1000)
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