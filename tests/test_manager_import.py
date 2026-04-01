"""测试知识管理器导入"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.core.knowledge.manager import KnowledgeBaseManager
    print("KnowledgeBaseManager 导入成功")
except ImportError as e:
    print(f"KnowledgeBaseManager 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("测试完成")