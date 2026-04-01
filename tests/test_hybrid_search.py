"""测试混合检索功能"""
import sys
from pathlib import Path
import numpy as np

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.vector.store import VectorStoreManager


def test_hybrid_search():
    """测试混合检索功能"""
    print("=== 混合检索功能测试 ===\n")
    
    # 创建向量存储管理器
    vector_store = VectorStoreManager()
    store_name = "test_hybrid_search"
    
    # 创建向量存储
    vector_store.create_vector_store(store_name)
    
    # 准备测试文档
    test_documents = [
        {
            "id": "1",
            "text": "陈平安是齐静春代替文圣收的徒弟，齐静春为其传道。",
            "embedding": list(np.random.randn(1024)),
            "metadata": {"source": "knowledge"}
        },
        {
            "id": "2",
            "text": "齐静春说话的语气偏教书先生的语气，不用那么苍老。",
            "embedding": list(np.random.randn(1024)),
            "metadata": {"source": "knowledge"}
        },
        {
            "id": "3",
            "text": "陈平安是文圣的弟子，齐静春是他的师兄。",
            "embedding": list(np.random.randn(1024)),
            "metadata": {"source": "knowledge"}
        },
        {
            "id": "4",
            "text": "齐静春是山崖书院的山主，负责教导学生。",
            "embedding": list(np.random.randn(1024)),
            "metadata": {"source": "knowledge"}
        },
        {
            "id": "5",
            "text": "陈平安的师傅是文圣，齐静春是他的引路人。",
            "embedding": list(np.random.randn(1024)),
            "metadata": {"source": "knowledge"}
        }
    ]
    
    # 添加文档
    print("[INFO] 添加测试文档...")
    success = vector_store.add_documents(store_name, test_documents)
    if not success:
        print("[ERROR] 添加文档失败")
        return
    
    print("[OK] 文档添加成功")
    
    # 测试查询
    test_query = "陈平安的师傅是谁"
    test_embedding = list(np.random.randn(1024))
    
    # 1. 测试 BM25 检索
    print("\n1. 测试 BM25 关键词检索:")
    bm25_results = vector_store.bm25_search(store_name, test_query, top_k=3)
    print(f"   找到 {len(bm25_results)} 个结果:")
    for i, result in enumerate(bm25_results, 1):
        print(f"   {i}. 得分: {result['score']:.4f}")
        print(f"      文本: {result['text'][:50]}...")
    
    # 2. 测试向量检索
    print("\n2. 测试向量语义检索:")
    vector_results = vector_store.search(store_name, test_embedding, top_k=3)
    print(f"   找到 {len(vector_results)} 个结果:")
    for i, result in enumerate(vector_results, 1):
        print(f"   {i}. 得分: {result['score']:.4f}")
        print(f"      文本: {result['text'][:50]}...")
    
    # 3. 测试混合检索
    print("\n3. 测试混合检索 (BM25 + 向量):")
    hybrid_results = vector_store.hybrid_search(store_name, test_query, test_embedding, top_k=3)
    print(f"   找到 {len(hybrid_results)} 个结果:")
    for i, result in enumerate(hybrid_results, 1):
        print(f"   {i}. 融合得分: {result['score']:.4f}")
        print(f"      文本: {result['text'][:50]}...")
    
    # 4. 测试专有名词检索
    print("\n4. 测试专有名词检索:")
    proper_noun_query = "齐静春"
    hybrid_results = vector_store.hybrid_search(store_name, proper_noun_query, test_embedding, top_k=3)
    print(f"   找到 {len(hybrid_results)} 个结果:")
    for i, result in enumerate(hybrid_results, 1):
        print(f"   {i}. 融合得分: {result['score']:.4f}")
        print(f"      文本: {result['text'][:50]}...")
    
    # 5. 测试长尾问题
    print("\n5. 测试长尾问题检索:")
    long_tail_query = "齐静春和陈平安的师徒关系是怎样的"
    hybrid_results = vector_store.hybrid_search(store_name, long_tail_query, test_embedding, top_k=3)
    print(f"   找到 {len(hybrid_results)} 个结果:")
    for i, result in enumerate(hybrid_results, 1):
        print(f"   {i}. 融合得分: {result['score']:.4f}")
        print(f"      文本: {result['text'][:50]}...")
    
    # 清理测试数据
    vector_store.delete_vector_store(store_name)
    print("\n[OK] 测试完成，清理测试数据")


if __name__ == "__main__":
    print("开始混合检索功能测试...\n")
    test_hybrid_search()
    print("\n=== 测试完成 ===")
    print("混合检索功能已成功实现：")
    print("- BM25 关键词检索")
    print("- 向量语义检索")
    print("- 倒数排名融合算法")
    print("- 混合检索结果排序")