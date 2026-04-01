"""测试运行脚本"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    
    tests = [
        ("异步任务队列系统", "tests.test_async_task_system"),
        ("混合检索", "tests.test_hybrid_search"),
        ("父子索引分块", "tests.test_parent_child_chunking"),
        ("长文本分块", "tests.test_long_text_chunking"),
        ("完整父子分块流程", "tests.test_complete_parent_child"),
        ("PDF 解析器", "tests.test_pdf_parser"),
        ("验证父子分块实现", "tests.verify_parent_child_implementation"),
    ]
    
    passed = 0
    failed = 0
    
    for name, module in tests:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"{'='*60}")
        try:
            __import__(module)
            passed += 1
            print(f"[OK] {name} 测试通过")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {name} 测试失败: {e}")
    
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    return failed == 0


def run_specific_test(test_name):
    """运行指定测试"""
    test_map = {
        "async": "tests.test_async_task_system",
        "hybrid": "tests.test_hybrid_search",
        "chunk": "tests.test_parent_child_chunking",
        "long_text": "tests.test_long_text_chunking",
        "complete": "tests.test_complete_parent_child",
        "pdf": "tests.test_pdf_parser",
        "verify": "tests.verify_parent_child_implementation",
    }
    
    if test_name in test_map:
        module = test_map[test_name]
        print(f"运行测试: {test_name}")
        try:
            __import__(module)
            return True
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    else:
        print(f"未知测试: {test_name}")
        print(f"可用测试: {', '.join(test_map.keys())}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
