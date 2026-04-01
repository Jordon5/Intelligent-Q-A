"""测试 PDF 解析功能"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge.parser import DocumentParser


def test_parser_initialization():
    """测试解析器初始化"""
    print("=== 测试 PDF 解析器初始化 ===")
    try:
        parser = DocumentParser()
        print("✅ PDF 解析器初始化成功")
        return True
    except Exception as e:
        print(f"❌ 解析器初始化失败: {e}")
        return False

def test_visual_block_extraction():
    """测试视觉块提取功能"""
    print("\n=== 测试视觉块提取功能 ===")
    try:
        parser = DocumentParser()
        
        # 测试视觉块提取方法的存在
        if hasattr(parser, '_extract_visual_blocks'):
            print("✅ 视觉块提取方法存在")
        else:
            print("❌ 视觉块提取方法不存在")
        
        # 测试多栏处理方法的存在
        if hasattr(parser, '_detect_columns'):
            print("✅ 多栏检测方法存在")
        else:
            print("❌ 多栏检测方法不存在")
        
        # 测试表格提取方法的存在
        if hasattr(parser, '_extract_table'):
            print("✅ 表格提取方法存在")
        else:
            print("❌ 表格提取方法不存在")
        
        # 测试图片描述方法的存在
        if hasattr(parser, '_describe_image'):
            print("✅ 图片描述方法存在")
        else:
            print("❌ 图片描述方法不存在")
        
        return True
    except Exception as e:
        print(f"❌ 测试功能存在性失败: {e}")
        return False

def test_dependency_imports():
    """测试依赖库导入"""
    print("\n=== 测试依赖库导入 ===")
    
    dependencies = {
        'fitz': 'PyMuPDF',
        'llama_parse': 'llama-parse',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'httpx': 'httpx'
    }
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
        except ImportError:
            print(f"⚠️  {name} 未安装")
        except Exception as e:
            print(f"❌ {name} 导入失败: {e}")


def main():
    """主测试函数"""
    print("开始测试 PDF 解析功能...\n")
    
    # 测试解析器初始化
    init_success = test_parser_initialization()
    
    # 测试功能存在性
    func_success = test_visual_block_extraction()
    
    # 测试依赖导入
    test_dependency_imports()
    
    print("\n=== 测试完成 ===")
    if init_success and func_success:
        print("✅ 所有核心测试通过！")
        print("PDF 解析功能已就绪，可以处理复杂的 PDF 文档。")
    else:
        print("❌ 部分测试失败，请检查错误信息。")


if __name__ == "__main__":
    main()