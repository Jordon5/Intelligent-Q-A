# 启动脚本

Write-Host "=== 万能问答框架启动脚本 ==="

# 检查 Python 版本
Write-Host "检查 Python 版本..."
python --version

# 安装依赖
Write-Host "安装依赖..."
pip install -r requirements.txt

# 创建必要的目录
Write-Host "创建必要的目录..."
New-Item -ItemType Directory -Path "data\knowledge" -Force
New-Item -ItemType Directory -Path "data\vector" -Force
New-Item -ItemType Directory -Path "data\tasks" -Force
New-Item -ItemType Directory -Path "config" -Force

# 启动 API 服务
Write-Host "启动 API 服务..."
Write-Host "服务将在 http://localhost:8000 上运行"
Write-Host "Web 界面地址: http://localhost:8000"
Write-Host "API 文档地址: http://localhost:8000/docs"
Write-Host "按 Ctrl+C 停止服务"

python -m app.api.main
