@echo off
chcp 65001 >nul
echo 正在启动 Redis...
echo Redis 路径: C:\Program Files\Redis\redis-server.exe
echo 配置文件: C:\Program Files\Redis\redis.windows.conf
echo.

"C:\Program Files\Redis\redis-server.exe" "C:\Program Files\Redis\redis.windows.conf"

if errorlevel 1 (
    echo 错误: 无法启动 Redis
    pause
    exit /b 1
)
