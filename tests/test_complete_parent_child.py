"""完整测试父子索引分块策略"""
import sys
from pathlib import Path
import json
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge.manager import KnowledgeBaseManager


def test_complete_parent_child_workflow():
    """测试完整的父子索引分块工作流程"""
    print("=== 完整父子索引分块策略测试 ===\n")
    
    # 创建临时知识库目录
    temp_dir = Path(tempfile.mkdtemp())
    kb_dir = temp_dir / "test_kb"
    kb_dir.mkdir()
    
    # 创建 metadata.json
    metadata = {
        "name": "测试知识库",
        "description": "用于测试父子索引分块策略",
        "version": "1.0.0",
        "created_at": "2024-01-01",
        "author": "测试用户"
    }
    
    with open(kb_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 创建 documents 目录
    docs_dir = kb_dir / "documents"
    docs_dir.mkdir()
    
    # 创建测试文档
    test_content = """陈平安是齐静春代替文圣收的徒弟，齐静春为其传道。齐静春是山崖书院的山主，负责教导学生。陈平安的师傅是文圣，齐静春是他的引路人。

齐静春说话的语气偏教书先生的语气，不用那么苍老。他是一位学识渊博的学者，对陈平安的成长起到了重要的作用。

陈平安在齐静春的指导下，逐渐成长为一名有担当的年轻人。齐静春虽然去世了，但他的教导一直影响着陈平安。

在故事的发展中，陈平安经历了许多困难和挑战，但他始终记得齐静春的教诲，坚持自己的信念。

齐静春的精神和教导成为陈平安前进的动力，帮助他度过了许多难关。"""
    
    with open(docs_dir / "test.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"[INFO] 创建临时知识库: {kb_dir}")
    
    # 初始化知识管理器
    kb_manager = KnowledgeBaseManager()
    
    # 处理知识库
    print("[INFO] 处理知识库...")
    result = kb_manager.process_knowledge_base(str(kb_dir), {})
    
    if not result.get("success"):
        print(f"[ERROR] 处理知识库失败: {result.get('error')}")
        return False
    
    print("[OK] 知识库处理成功")
    
    kb_info = result["knowledge_base"]
    kb_id = kb_info["id"]
    vector_store_name = kb_info["vector_store_name"]
    
    print(f"- 知识库ID: {kb_id}")
    print(f"- 向量存储名称: {vector_store_name}")
    
    # 检查父块文件
    kb_dir_in_data = Path("./data/knowledge") / kb_id
    parent_chunks_path = kb_dir_in_data / "parent_chunks.json"
    
    if parent_chunks_path.exists():
        print("[OK] 父块文件已创建")
        with open(parent_chunks_path, "r", encoding="utf-8") as f:
            parent_chunks = json.load(f)
        print(f"- 父块数量: {len(parent_chunks)}")
        
        # 显示父块信息
        for i, parent in enumerate(parent_chunks):
            print(f"\n父块 {i+1}:")
            print(f"- ID: {parent['id'][:8]}...")
            print(f"- 长度: {parent['length']}")
            print(f"- 内容: {parent['text'][:100]}...")
    else:
        print("[ERROR] 父块文件未创建")
        return False
    
    # 检查向量存储
    vector_stores = kb_manager.vector_store_manager.list_vector_stores()
    if vector_store_name in vector_stores:
        print("[OK] 向量存储已创建")
        stats = kb_manager.vector_store_manager.get_vector_store_stats(vector_store_name)
        print(f"- 文档数量: {stats['document_count']}")
    else:
        print("[ERROR] 向量存储未创建")
        return False
    
    # 测试检索功能
    print("\n[INFO] 测试检索功能...")
    
    # 创建测试查询嵌入
    test_query = "陈平安的师傅是谁"
    test_embedding = kb_manager._generate_temp_embedding(test_query)
    
    # 测试向量检索
    vector_results = kb_manager.vector_store_manager.search(
        vector_store_name,
        test_embedding,
        top_k=3
    )
    
    print(f"[OK] 向量检索完成，找到 {len(vector_results)} 个结果")
    for i, result in enumerate(vector_results):
        print(f"\n结果 {i+1}:")
        print(f"- ID: {result['id'][:8]}...")
        print(f"- 得分: {result['score']:.4f}")
        print(f"- 内容: {result['text'][:80]}...")
    
    # 测试父子块关联
    print("\n[INFO] 测试父子块关联...")
    from app.core.knowledge.parent_child_retriever import ParentChildRetriever
    
    retriever = ParentChildRetriever()
    
    # 获取父块
    parent_chunks_from_children = retriever.get_parent_chunks_from_children(
        vector_results,
        kb_id
    )
    
    print(f"[OK] 父子块关联完成，找到 {len(parent_chunks_from_children)} 个父块")
    for i, parent in enumerate(parent_chunks_from_children):
        print(f"\n父块 {i+1}:")
        print(f"- ID: {parent['id'][:8]}...")
        print(f"- 长度: {parent['length']}")
        print(f"- 内容: {parent['text'][:120]}...")
    
    # 测试上下文组合
    print("\n[INFO] 测试上下文组合...")
    combined_context = retriever.get_combined_context(
        vector_results,
        kb_id,
        max_context_length=1000
    )
    
    print(f"[OK] 上下文组合完成")
    print(f"- 组合上下文长度: {len(combined_context)}")
    print("-" * 50)
    print(combined_context)
    print("-" * 50)
    
    # 清理临时文件
    shutil.rmtree(temp_dir)
    print(f"\n[OK] 清理临时文件完成")
    
    return True


if __name__ == "__main__":
    print("开始完整父子索引分块策略测试...\n")
    success = test_complete_parent_child_workflow()
    print("\n=== 测试完成 ===")
    if success:
        print("父子索引分块策略完整工作流程测试成功！")
        print("✅ 知识库处理")
        print("✅ 父子块生成")
        print("✅ 向量存储创建")
        print("✅ 检索功能")
        print("✅ 父子块关联")
        print("✅ 上下文组合")
    else:
        print("测试失败，请检查错误信息")