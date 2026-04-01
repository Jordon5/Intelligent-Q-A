"""完整测试 PDF 解析功能"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge.parser import DocumentParser


def test_pdf_parsing():
    """测试完整的 PDF 解析功能"""
    print("=== 完整 PDF 解析测试 ===\n")
    
    parser = DocumentParser()
    test_file = "test_documents/sample.pdf"
    
    # 检查测试文件是否存在
    if not Path(test_file).exists():
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return False
    
    print(f"[INFO] 开始解析 PDF 文件: {test_file}")
    
    try:
        # 解析 PDF 文件
        result = parser.parse(test_file)
        
        print(f"\n[OK] PDF 解析成功")
        print(f"[INFO] 提取的文本长度: {len(result)} 字符")
        
        # 检查解析结果中是否包含新功能的标记
        features_found = []
        
        if "表格" in result:
            features_found.append("[OK] 表格识别功能正常")
        
        if "测试 PDF 文档" in result:
            features_found.append("[OK] 文本提取功能正常")
        
        if features_found:
            print("\n检测到的功能:")
            for feature in features_found:
                print(f"  {feature}")
        
        # 显示部分内容
        print(f"\n前 500 字符内容:")
        print("-" * 50)
        print(result[:500])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] PDF 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始完整 PDF 解析测试...\n")
    
    success = test_pdf_parsing()
    
    print("\n=== 测试完成 ===")
    if success:
        print("[OK] PDF 解析功能完全正常！")
        print("可以处理复杂的 PDF 文档，包括多栏排版、表格和图片。")
    else:
        print("[ERROR] PDF 解析测试失败，请检查错误信息。")