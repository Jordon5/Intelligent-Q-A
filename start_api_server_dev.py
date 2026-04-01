"""启动 FastAPI 服务（开发模式 - 使用 fakeredis）"""
import os

# 设置开发模式
os.environ['DEV_MODE'] = 'true'

import uvicorn
from app.api.main import app

if __name__ == '__main__':
    print("=" * 60)
    print("Starting API Server (Development Mode)")
    print("Using fakeredis (No Redis server needed)")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
