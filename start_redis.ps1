# 启动 Redis 脚本
# Redis 安装在 C:\Program Files\Redis

$redisPath = "C:\Program Files\Redis\redis-server.exe"
$configPath = "C:\Program Files\Redis\redis.windows.conf"

if (Test-Path $redisPath) {
    Write-Host "Starting Redis..." -ForegroundColor Green
    Write-Host "Redis Path: $redisPath" -ForegroundColor Gray
    Write-Host "Config File: $configPath" -ForegroundColor Gray
    Write-Host ""
    
    # 启动 Redis
    & $redisPath $configPath
} else {
    Write-Host "Error: Redis server not found" -ForegroundColor Red
    Write-Host "Please check if Redis is installed at: $redisPath" -ForegroundColor Yellow
    exit 1
}
