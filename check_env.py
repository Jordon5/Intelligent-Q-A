"""环境检查脚本"""
import sys

def check_environment():
    """检查当前 Python 环境"""
    print("=" * 60)
    print("Python Environment Check")
    print("=" * 60)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print()
    
    # 检查关键依赖
    critical_deps = [
        "fastapi",
        "uvicorn", 
        "celery",
        "redis",
        "aiofiles",
    ]
    
    print("Checking critical dependencies:")
    missing = []
    
    for dep in critical_deps:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', 'unknown')
            print(f"  [OK] {dep}: {version}")
        except ImportError as e:
            print(f"  [MISSING] {dep}")
            missing.append(dep)
    
    print()
    
    # 尝试检查 chromadb（可能有问题）
    try:
        import chromadb
        print(f"  [OK] chromadb: {chromadb.__version__}")
    except ImportError:
        print(f"  [MISSING] chromadb")
        missing.append("chromadb")
    except Exception as e:
        print(f"  [WARNING] chromadb: Import error - {e}")
    
    print()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install: pip install -r requirements.txt")
        return False
    else:
        print("All critical dependencies are installed!")
        print("You can now start the server with: python start_api_server.py")
        return True

if __name__ == '__main__':
    success = check_environment()
    sys.exit(0 if success else 1)
