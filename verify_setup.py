#!/usr/bin/env python3
"""验证基础框架设置"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from src.config import get_settings
from src.utils.markdown import markdown_to_text, extract_metadata
from src.utils.chunking import TextChunker


def test_config():
    """测试配置"""
    print("测试配置模块...")
    settings = get_settings()
    print(f"✅ 配置加载成功: {settings.character_name}")


def test_markdown():
    """测试 Markdown 处理"""
    print("\n测试 Markdown 处理...")
    test_md = """---
title: 测试文档
context: test
---

# 测试标题

这是一个测试段落。
包含多行内容。
"""
    text = markdown_to_text(test_md)
    metadata = extract_metadata(test_md)
    print(f"✅ 文本提取: {text[:50]}...")
    print(f"✅ 元数据提取: {metadata}")


def test_chunking():
    """测试文本分块"""
    print("\n测试文本分块...")
    test_text = "这是一个测试文本。" * 20  # 生成较长文本
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk(test_text, {"source": "test"})
    print(f"✅ 分块结果: {len(chunks)} 块")
    for i, chunk in enumerate(chunks):
        print(f"   块 {i+1}: {len(chunk['text'])} 字符")


def main():
    """主函数"""
    try:
        test_config()
        test_markdown()
        test_chunking()
        print("\n🎉 基础框架验证通过！")
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()