#!/usr/bin/env python3
"""测试 RAG 引擎"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from src.config import get_settings
from src.llm import create_qwen_provider
from src.vector_store import create_chroma_vector_store, VectorDocument
from src.rag import create_rag_engine, CharacterProfile


async def test_rag_engine():
    """测试 RAG 引擎"""
    print("测试 RAG 引擎...")
    settings = get_settings()
    
    # 检查 API 密钥
    if not settings.qwen_api_key:
        print("⚠️  QWEN_API_KEY 未配置，跳过 RAG 测试")
        return
    
    # 初始化组件
    llm_provider = create_qwen_provider(
        api_key=settings.qwen_api_key,
        chat_model=settings.qwen_chat_model,
        embed_model=settings.qwen_embed_model,
        base_url=settings.qwen_chat_base,
        embed_dim=settings.embed_dim,
    )
    
    vector_store = create_chroma_vector_store(
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection_name,
        embedding_dim=settings.embed_dim,
    )
    
    try:
        # 清空并添加测试文档
        await vector_store.clear_all()
        
        # 生成嵌入
        test_texts = ["齐静春是儒家圣人文圣的弟子", "齐静春曾担任山崖书院的山主"]
        embed_response = await llm_provider.embed(test_texts)
        
        # 添加文档
        documents = []
        for i, (text, embedding) in enumerate(zip(test_texts, embed_response.embeddings)):
            doc = VectorDocument(
                id=f"test{i+1}",
                text=text,
                vector=embedding,
                metadata={"source": "test", "character": "齐静春"},
            )
            documents.append(doc)
        
        await vector_store.add_documents(documents)
        print(f"✅ 添加测试文档成功: {len(documents)} 个")
        
        # 创建人物配置
        character_profile = CharacterProfile(
            name="齐静春",
            era="儒家圣人时代",
            personality="温和儒雅，胸有丘壑，悲天悯人",
            speaking_style="言语温和，引经据典，有长者之风",
            background="文圣弟子，曾任山崖书院山主",
        )
        
        # 创建 RAG 引擎
        rag_engine = create_rag_engine(
            llm_provider=llm_provider,
            vector_store=vector_store,
            character_profile=character_profile,
            top_k=2,
            use_character_mode=True,
        )
        
        # 测试提问
        question = "齐静春是谁？"
        print(f"\n测试提问: {question}")
        
        response = await rag_engine.ask(question)
        print(f"✅ 回答: {response.answer}")
        print(f"   来源数量: {len(response.sources)}")
        print(f"   使用回退: {response.used_fallback}")
        
        # 测试对话
        print("\n测试对话...")
        history = [
            {"role": "user", "content": "你好，请问你是谁？"},
            {"role": "assistant", "content": "我是齐静春，文圣弟子。"},
        ]
        
        follow_up_question = "你曾经在哪里任职？"
        response2 = await rag_engine.chat(follow_up_question, history=history)
        print(f"✅ 追问: {follow_up_question}")
        print(f"✅ 回答: {response2.answer}")
        
    finally:
        await llm_provider.close()
        # 清空测试数据
        await vector_store.clear_all()


async def main():
    """主函数"""
    try:
        await test_rag_engine()
        print("\n🎉 RAG 引擎测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())