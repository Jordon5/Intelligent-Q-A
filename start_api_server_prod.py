"""启动 FastAPI 服务（生产模式 - 使用真实 Redis）"""
import os

# 确保使用真实 Redis
if 'DEV_MODE' in os.environ:
    del os.environ['DEV_MODE']

import uvicorn
from app.api.main import app

if __name__ == '__main__':
    print("=" * 60)
    print("Starting API Server (Production Mode)")
    print("Using Real Redis at localhost:6379")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
