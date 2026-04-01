"""测试配置模块"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import get_settings

def test_get_settings():
    """测试配置加载"""
    print("测试配置加载")
    settings = get_settings()

    print(f"API 服务：{settings.api_host}:{settings.api_port}")
    print(f"人物名称：{settings.character_name}")
    print(f"人物时代：{settings.character_era}")
    print(f"向量存储：{settings.vector_store_type}")
    print(f"嵌入维度：{settings.embed_dim}")


    # 检查是否存在必要配置
    assert settings.qwen_api_key, "Qwen API 密钥未配置"
    assert settings.character_name, "人物名称未配置"

    print("测试配置加载完成")

if __name__ == "__main__":
    test_get_settings()