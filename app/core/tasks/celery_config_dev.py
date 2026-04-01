"""Celery 开发配置 - 使用 fakeredis 替代真实 Redis"""
from celery import Celery
import os

# 开发环境使用 fakeredis
try:
    import fakeredis
    # 创建 fakeredis 服务器
    fake_redis_server = fakeredis.FakeServer()
    redis_url = 'redis://localhost:6379/0'
    
    # 设置环境变量，让 celery 使用 fakeredis
    os.environ['CELERY_BROKER_URL'] = redis_url
    os.environ['CELERY_RESULT_BACKEND'] = redis_url
    
    print("[INFO] 使用 fakeredis 作为 Redis 替代（开发环境）")
except ImportError:
    # 如果没有 fakeredis，使用内存后端
    redis_url = 'memory://'
    print("[WARNING] 未安装 fakeredis，使用内存后端（数据不会持久化）")

# 创建 Celery 应用
celery_app = Celery(
    'rag_chatbot',
    broker=redis_url,
    backend=redis_url,
    include=['app.core.tasks.celery_tasks']
)

# Celery 配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    task_soft_time_limit=3000,  # 50分钟软超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    # 开发环境配置
    task_always_eager=True,  # 同步执行任务（开发环境）
    task_store_eager_result=True,
)

if __name__ == '__main__':
    celery_app.start()
