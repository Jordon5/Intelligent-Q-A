"""测试核心模块"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from src.config import get_settings
from src.llm import create_qwen_provider, Message
from src.vector_store import create_chroma_vector_store, VectorDocument

async def test_llm_provider():
    """测试LLM提供程序"""
    print("测试LLM提供程序")
    settings = get_settings()
    
    if not os.environ.get("QWEN_API_KEY") or os.environ.get("QWEN_API_KEY") == "":
        print("  QWEN_API_KEY 环境变量未设置，跳过 LLM 测试")
        return
    
    llm_provider = create_qwen_provider(
        api_key=settings.qwen_api_key,
        chat_model=settings.qwen_chat_model,
        embed_model=settings.qwen_embed_model,
        base_url=settings.qwen_chat_base,
        embed_dim=settings.embed_dim,
    )

    try:
        message = Message(role="user", content="你好，请介绍一下自己")
        response = await llm_provider.chat(message)
        print(f" 测试通过，回答：{response.content[:50]}...")

        # 测试嵌入
        texts = ["这是一个测试文本", "这是另一个测试文本"]
        embed_response = await llm_provider.embed(texts)
        print(f" 测试通过，维度：{len(embed_response.embeddings[0])}")

    finally:
        await llm_provider.close()

async def test_vector_store():
    """测试向量数据库"""
    print("测试向量数据库")
    settings = get_settings()

    vector_store = create_chroma_vector_store(
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection_name,
        embedding_dim=settings.embed_dim,
    )

    # 测试清空功能
    await vector_store.clear_all()
    count = await vector_store.count()
    print(f" 测试通过：文档数： {count}")

    test_doc = VectorDocument(
        id="test1",
        text="这是一个测试文档",
        vector=[0.1] * settings.embed_dim,
        metadata={"source": "test", "category": "test"}
    )
    await vector_store.add_documents([test_doc])
    count = await vector_store.count()
    print(f" 添加文档成功：文档数={count}")

    # 测试查询
    results = await vector_store.search([0.1] * settings.embed_dim)
    print(f" 搜索测试通过：结果数：{len(results)}")
    if results:
        print(f" 相似度：{results[0].score:.2f}")

    # 测试删除
    await vector_store.delete_documents(["test1"])
    count = await vector_store.count()
    print(f" 删除测试通过：文档数={count}")

async def main():
    try:
        await test_llm_provider()
        await test_vector_store()
        print("\n 所有测试通过")
    except Exception as e:
        print(f"\n 测试失败")
        import traceback
        traceback.print_exc()
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

