"""测试 PDF 解析的高级功能"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge.parser import DocumentParser


def test_pdf_parser():
    """测试 PDF 解析功能"""
    print("=== PDF 解析高级功能测试 ===\n")
    
    parser = DocumentParser()
    
    # 测试文件路径（如果存在）
    test_files = [
        "test_documents/sample.pdf",
        "test_documents/multi_column.pdf",
        "test_documents/with_tables.pdf",
        "test_documents/scanned.pdf"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if not file_path.exists():
            print(f"[警告] 测试文件不存在: {test_file}")
            continue
        
        print(f"[文件] 测试文件: {test_file}")
        print("-" * 50)
        
        try:
            result = parser.parse(str(file_path))
            
            # 检查结果中是否包含新功能的标记
            features_found = []
            
            if "[图片:" in result:
                features_found.append("[OK] 图片检测")
            
            if "[表格" in result:
                features_found.append("[OK] 表格识别")
            
            if "[OCR 处理结果]" in result:
                features_found.append("[OK] OCR 处理")
            
            if features_found:
                print("检测到的功能:")
                for feature in features_found:
                    print(f"  {feature}")
            else:
                print("[信息] 基本文本提取")
            
            # 显示部分内容
            print(f"\n提取的文本长度: {len(result)} 字符")
            print(f"前 200 字符:\n{result[:200]}...")
            
        except Exception as e:
            print(f"[错误] 解析失败: {str(e)}")
        
        print("\n" + "=" * 50 + "\n")
    
    print("=== 测试完成 ===")


def test_pdf_parser_with_sample():
    """使用示例文本测试 PDF 解析器"""
    print("=== PDF 解析器功能测试 ===\n")
    
    parser = DocumentParser()
    
    # 测试多栏排版检测
    print("[测试] 多栏排版检测:")
    test_words = [
        {'x0': 10, 'top': 100, 'text': '第一列文本1'},
        {'x0': 10, 'top': 120, 'text': '第一列文本2'},
        {'x0': 10, 'top': 140, 'text': '第一列文本3'},
        {'x0': 10, 'top': 160, 'text': '第一列文本4'},
        {'x0': 10, 'top': 180, 'text': '第一列文本5'},
        {'x0': 400, 'top': 100, 'text': '第二列文本1'},
        {'x0': 400, 'top': 120, 'text': '第二列文本2'},
        {'x0': 400, 'top': 140, 'text': '第二列文本3'},
        {'x0': 400, 'top': 160, 'text': '第二列文本4'},
        {'x0': 400, 'top': 180, 'text': '第二列文本5'},
    ]
    
    is_multi = parser._is_multi_column(test_words)
    print(f"  多栏检测结果: {'[OK] 检测到多栏' if is_multi else '[FAIL] 未检测到多栏'}")
    
    # 测试 OCR 需求判断
    print("\n[测试] OCR 需求判断:")
    
    empty_text = ""
    needs_ocr1 = parser._needs_ocr(empty_text)
    print(f"  空文本需要OCR: {'[OK] 是' if needs_ocr1 else '[FAIL] 否'}")
    
    short_text = "测试"
    needs_ocr2 = parser._needs_ocr(short_text)
    print(f"  短文本需要OCR: {'[OK] 是' if needs_ocr2 else '[FAIL] 否'}")
    
    normal_text = "这是一段正常的文本内容，包含足够的字符和合理的结构。这段文本应该足够长，不需要进行OCR处理。我们继续添加更多的中文内容，确保文本长度超过50个字符，并且包含足够的中文单词。这样就能正确判断不需要进行OCR处理了。"
    needs_ocr3 = parser._needs_ocr(normal_text)
    print(f"  正常文本需要OCR: {'[OK] 否' if not needs_ocr3 else '[FAIL] 是'}")
    
    # 测试表格处理
    print("\n[测试] 表格处理:")
    test_tables = [
        [
            ["姓名", "年龄", "城市"],
            ["张三", "25", "北京"],
            ["李四", "30", "上海"]
        ]
    ]
    
    table_result = parser._process_tables(test_tables)
    print(f"  表格处理结果:\n{table_result}")
    
    print("\n=== 功能测试完成 ===")


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 测试实际 PDF 文件")
    print("2. 测试解析器功能")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        test_pdf_parser()
    elif choice == "2":
        test_pdf_parser_with_sample()
    else:
        print("无效的选择，运行功能测试...")
        test_pdf_parser_with_sample()