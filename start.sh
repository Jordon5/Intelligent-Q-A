#!/bin/bash

# 启动脚本

echo "=== 万能问答框架启动脚本 ==="

# 检查 Python 版本
echo "检查 Python 版本..."
python --version

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p data/knowledge data/vector data/tasks config

# 启动 API 服务
echo "启动 API 服务..."
echo "服务将在 http://localhost:8000 上运行"
echo "Web 界面地址: http://localhost:8000"
echo "API 文档地址: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"

python -m app.api.main
