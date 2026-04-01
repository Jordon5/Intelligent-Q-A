"""开发环境启动脚本

使用 fakeredis 替代真实 Redis，方便开发和测试
"""
import sys
import os

# 设置开发环境标志
os.environ['DEV_MODE'] = 'true'

# 使用开发环境配置
from app.core.tasks.celery_config_dev import celery_app

if __name__ == '__main__':
    print("=" * 60)
    print("开发环境启动")
    print("=" * 60)
    print("使用 fakeredis 替代真实 Redis")
    print("任务将同步执行（无需启动 Worker）")
    print("=" * 60)
    
    # 启动 Celery
    celery_app.start()
