# 开发环境设置指南

## 问题：Redis 未安装

如果在 Windows 上运行 `redis-server` 提示命令未找到，说明 Redis 没有安装或没有添加到系统 PATH。

## 解决方案

### 方案一：使用 fakeredis（推荐，用于开发测试）

我们已经在项目中集成了 `fakeredis`，这是一个纯 Python 实现的 Redis 替代品，无需安装真实的 Redis 服务器。

**优点：**
- 无需安装 Redis
- 无需配置环境
- 数据存储在内存中，重启后清空
- 适合开发和测试

**使用方法：**

1. **安装依赖**（已安装）
```bash
pip install fakeredis
```

2. **启动开发环境**
```bash
# 设置开发环境变量并启动
set DEV_MODE=true
python start_api_server.py
```

或者在 PowerShell 中：
```powershell
$env:DEV_MODE="true"
python start_api_server.py
```

3. **直接运行测试**
```bash
# 测试不需要 Redis 服务
python -m tests.test_async_task_system
python -m tests.test_hybrid_search
python -m tests.test_parent_child_chunking
```

### 方案二：安装 Redis for Windows

**方法 1：使用 Chocolatey（推荐）**

1. 以管理员身份打开 PowerShell
2. 安装 Chocolatey（如果未安装）
3. 安装 Redis：
```powershell
choco install redis-64
```
4. 启动 Redis：
```powershell
redis-server
```

**方法 2：手动安装**

1. 下载 Redis for Windows：
   - 访问：https://github.com/microsoftarchive/redis/releases
   - 下载 `Redis-x64-xxx.msi`

2. 运行安装程序，按提示完成安装

3. 启动 Redis 服务：
   - 方式 1：在服务管理器中启动 Redis 服务
   - 方式 2：命令行启动：
   ```powershell
   redis-server
   ```

**方法 3：使用 WSL（Windows Subsystem for Linux）**

1. 安装 WSL（如果未安装）
2. 在 WSL 中安装 Redis：
```bash
sudo apt-get update
sudo apt-get install redis-server
```
3. 启动 Redis：
```bash
sudo service redis-server start
```

### 方案三：使用 Docker

如果您有 Docker 环境，可以使用 Docker 运行 Redis：

```bash
# 拉取 Redis 镜像
docker pull redis

# 运行 Redis 容器
docker run -d -p 6379:6379 --name redis redis

# 查看运行状态
docker ps

# 停止 Redis
docker stop redis

# 启动 Redis
docker start redis
```

## 生产环境建议

在生产环境中，建议使用真实的 Redis 服务器：

1. **Linux 服务器**：直接安装 Redis
2. **云服务**：使用云厂商提供的 Redis 服务（如阿里云 Redis、AWS ElastiCache）
3. **Docker**：使用 Docker 部署 Redis

## 配置文件说明

### 开发环境配置
- `app/core/tasks/celery_config_dev.py` - 使用 fakeredis 的配置
- `start_dev.py` - 开发环境启动脚本

### 生产环境配置
- `app/core/tasks/celery_config.py` - 使用真实 Redis 的配置
- `.env` - 环境变量配置

## 快速开始（开发环境）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置开发环境变量
set DEV_MODE=true  # Windows CMD
$env:DEV_MODE="true"  # PowerShell

# 3. 启动 API 服务
python start_api_server.py

# 4. 在另一个终端运行测试
python -m tests.test_async_task_system
```

## 常见问题

### Q: fakeredis 和真实 Redis 有什么区别？
A: fakeredis 是纯 Python 实现的内存数据库，功能与 Redis 兼容，但数据不会持久化，重启后丢失。适合开发和测试，不适合生产环境。

### Q: 如何切换到真实 Redis？
A: 取消设置 `DEV_MODE` 环境变量，或者设置为 `false`，系统会自动使用真实 Redis 配置。

### Q: 测试时需要启动 Redis 吗？
A: 如果使用 fakeredis（DEV_MODE=true），不需要启动 Redis。如果使用真实 Redis，需要先启动 Redis 服务。

### Q: Celery Worker 在开发环境需要启动吗？
A: 在开发环境（DEV_MODE=true）中，任务会同步执行，不需要启动 Celery Worker。在生产环境中，需要启动 Worker 来处理异步任务。
