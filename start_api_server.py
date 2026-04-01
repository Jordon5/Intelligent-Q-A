"""启动 FastAPI 服务"""
import os

# 清除可能存在的 DEV_MODE 环境变量（默认使用真实 Redis）
# 如果需要使用开发模式，请运行: start_api_server_dev.py
if os.getenv('DEV_MODE') is None:
    # 默认使用真实 Redis
    pass

import uvicorn
from app.api.main import app

if __name__ == '__main__':
    mode = "Development (fakeredis)" if os.getenv('DEV_MODE') == 'true' else "Production (Redis)"
    
    print("=" * 60)
    print(f"Starting API Server - {mode}")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
