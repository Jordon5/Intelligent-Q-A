"""启动 Celery Worker"""
from app.core.tasks.celery_config import celery_app

if __name__ == '__main__':
    celery_app.start()