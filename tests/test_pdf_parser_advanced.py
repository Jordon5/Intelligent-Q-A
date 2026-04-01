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
        "test_documents/with_images.pdf",
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
            
            if "[图片" in result:
                features_found.append("[OK] 图片检测")
            
            if "[表格" in result:
                features_found.append("[OK] 表格识别")
            
            if "[图片描述" in result:
                features_found.append("[OK] 图片描述")
            
            if features_found:
                print("检测到的功能:")
                for feature in features_found:
                    print(f"  {feature}")
            else:
                print("[信息] 基本文本提取")
            
            # 显示部分内容
            print(f"\n提取的文本长度: {len(result)} 字符")
            print(f"前 300 字符:\n{result[:300]}...")
            
        except Exception as e:
            print(f"[错误] 解析失败: {str(e)}")
        
        print("\n" + "=" * 50 + "\n")
    
    print("=== 测试完成 ===")


def test_visual_blocks():
    """测试视觉块识别功能"""
    print("=== 视觉块识别测试 ===\n")
    
    try:
        import fitz
        
        # 打开测试 PDF
        test_file = "test_documents/sample.pdf"
        file_path = Path(test_file)
        
        if not file_path.exists():
            print(f"[警告] 测试文件不存在: {test_file}")
            return
        
        with fitz.open(test_file) as pdf:
            page = pdf[0]  # 第一页
            
            # 测试视觉块提取
            parser = DocumentParser()
            blocks = parser._extract_visual_blocks(page)
            
            print(f"[信息] 提取到 {len(blocks)} 个视觉块")
            
            for i, block in enumerate(blocks):
                print(f"\n块 {i+1}:")
                print(f"  类型: {block['type']}")
                print(f"  边界框: {block['bbox']}")
                if block['type'] == "text":
                    print(f"  内容: {block['content'][:100]}...")
                elif block['type'] == "image":
                    print(f"  图片 XREF: {block.get('xref', 'N/A')}")
            
    except Exception as e:
        print(f"[错误] 测试失败: {str(e)}")
    
    print("\n=== 视觉块测试完成 ===")


def test_table_extraction():
    """测试表格提取功能"""
    print("=== 表格提取测试 ===\n")
    
    parser = DocumentParser()
    
    # 测试文件路径
    test_file = "test_documents/with_tables.pdf"
    file_path = Path(test_file)
    
    if not file_path.exists():
        print(f"[警告] 测试文件不存在: {test_file}")
        return
    
    try:
        # 测试表格提取
        table_content = parser._extract_table(file_path, 1)
        
        if table_content:
            print("[OK] 成功提取表格:")
            print(table_content)
        else:
            print("[警告] 未提取到表格")
            
    except Exception as e:
        print(f"[错误] 表格提取失败: {str(e)}")
    
    print("\n=== 表格提取测试完成 ===")


def test_image_description():
    """测试图片描述功能"""
    print("=== 图片描述测试 ===\n")
    
    parser = DocumentParser()
    
    # 测试文件路径
    test_file = "test_documents/with_images.pdf"
    file_path = Path(test_file)
    
    if not file_path.exists():
        print(f"[警告] 测试文件不存在: {test_file}")
        return
    
    try:
        import fitz
        
        with fitz.open(test_file) as pdf:
            page = pdf[0]  # 第一页
            
            # 提取视觉块
            blocks = parser._extract_visual_blocks(page)
            
            # 找到图片块
            image_blocks = [b for b in blocks if b['type'] == 'image']
            
            if image_blocks:
                print(f"[信息] 找到 {len(image_blocks)} 个图片块")
                
                for i, img_block in enumerate(image_blocks):
                    print(f"\n图片 {i+1}:")
                    print(f"  边界框: {img_block['bbox']}")
                    
                    # 生成图片描述
                    description = parser._describe_image(file_path, img_block['page_num'], img_block['bbox'])
                    print(f"  描述: {description}")
            else:
                print("[警告] 未找到图片块")
                
    except Exception as e:
        print(f"[错误] 图片描述测试失败: {str(e)}")
    
    print("\n=== 图片描述测试完成 ===")


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 测试完整 PDF 解析")
    print("2. 测试视觉块识别")
    print("3. 测试表格提取")
    print("4. 测试图片描述")
    print("5. 运行所有测试")
    
    choice = input("请输入选择 (1-5): ").strip()
    
    if choice == "1":
        test_pdf_parser()
    elif choice == "2":
        test_visual_blocks()
    elif choice == "3":
        test_table_extraction()
    elif choice == "4":
        test_image_description()
    elif choice == "5":
        test_pdf_parser()
        test_visual_blocks()
        test_table_extraction()
        test_image_description()
    else:
        print("无效的选择，运行完整测试...")
        test_pdf_parser()