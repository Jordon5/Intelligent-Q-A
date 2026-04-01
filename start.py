#!/usr/bin/env python
"""
万能问答框架 - 统一启动脚本

使用方法:
    python start.py                    # 生产模式（需要 Redis）
    python start.py --dev              # 开发模式（使用 fakeredis）
    python start.py --redis            # 启动 Redis 服务
    python start.py --worker           # 启动 Celery Worker
    python start.py --all              # 启动所有服务（Redis + Worker + API）
    python start.py --all --dev        # 开发模式启动所有服务
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def start_redis():
    """启动 Redis 服务"""
    redis_path = Path("C:/Program Files/Redis/redis-server.exe")
    config_path = Path("C:/Program Files/Redis/redis.windows.conf")
    
    if not redis_path.exists():
        print("[ERROR] Redis 未安装")
        print("请安装 Redis 或使用开发模式: python start.py --dev")
        return False
    
    print("[INFO] 启动 Redis 服务...")
    subprocess.Popen(
        [str(redis_path), str(config_path)],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    return True


def start_celery_worker():
    """启动 Celery Worker"""
    print("[INFO] 启动 Celery Worker...")
    subprocess.Popen(
        [sys.executable, "start_celery_worker.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    return True


def start_api_server(dev_mode=False):
    """启动 API 服务"""
    if dev_mode:
        os.environ['DEV_MODE'] = 'true'
        print("[INFO] 启动 API 服务（开发模式 - fakeredis）...")
    else:
        if 'DEV_MODE' in os.environ:
            del os.environ['DEV_MODE']
        print("[INFO] 启动 API 服务（生产模式 - Redis）...")
    
    import uvicorn
    from app.api.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )


def main():
    parser = argparse.ArgumentParser(
        description="万能问答框架启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python start.py                  # 生产模式启动 API
    python start.py --dev            # 开发模式启动 API
    python start.py --all            # 启动所有服务
    python start.py --all --dev      # 开发模式启动所有服务
        """
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='开发模式（使用 fakeredis，无需 Redis 服务）'
    )
    parser.add_argument(
        '--redis',
        action='store_true',
        help='启动 Redis 服务'
    )
    parser.add_argument(
        '--worker',
        action='store_true',
        help='启动 Celery Worker'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='启动所有服务（Redis + Worker + API）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("万能问答框架")
    print("=" * 60)
    print()
    
    # 启动所有服务
    if args.all:
        if not args.dev:
            start_redis()
            import time
            time.sleep(2)
            start_celery_worker()
            time.sleep(2)
        start_api_server(dev_mode=args.dev)
        return
    
    # 单独启动 Redis
    if args.redis:
        start_redis()
        return
    
    # 单独启动 Worker
    if args.worker:
        start_celery_worker()
        return
    
    # 默认启动 API 服务
    start_api_server(dev_mode=args.dev)


if __name__ == '__main__':
    main()
