# 异步任务队列系统

基于 FastAPI + Celery + Redis 的异步任务队列系统，支持断点续传与任务状态轮询。

## 功能特性

- ✅ 基于 FastAPI 的异步 RESTful 服务
- ✅ 利用 Celery + Redis 实现任务队列
- ✅ 支持断点续传与任务状态轮询
- ✅ 确保系统在并发上传大文件时的稳定性
- ✅ 文件上传与 API 服务的解耦
- ✅ 耗时文档解析任务的异步处理

## 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client   │────▶│  FastAPI   │────▶│   Redis    │
│             │     │   Server    │     │   Broker    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                      │
                           ▼                      ▼
                      ┌─────────────┐     ┌─────────────┐
                      │   Celery    │────▶│  Celery     │
                      │   Worker    │     │  Tasks      │
                      └─────────────┘     └─────────────┘
```

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `celery>=5.3.0` - 异步任务队列
- `redis>=5.0.0` - 消息代理和结果存储
- `aiofiles>=23.0.0` - 异步文件操作

## 配置

1. 复制环境配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置 Redis 连接：
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

3. 配置应用参数：
```env
APP_HOST=0.0.0.0
APP_PORT=8000
MAX_FILE_SIZE=104857600  # 100MB
CHUNK_SIZE=5242880  # 5MB
```

## 启动服务

### 1. 启动 Redis

```bash
# Windows
redis-server

# Linux/Mac
redis-server
```

### 2. 启动 Celery Worker

```bash
python start_celery_worker.py
```

### 3. 启动 FastAPI 服务

```bash
python start_api_server.py
```

## API 接口

### 文件上传接口

#### 1. 初始化上传会话

```http
POST /api/files/upload/init
Content-Type: multipart/form-data

参数：
- file_name: 文件名
- file_size: 文件大小（字节）
- file_hash: 文件哈希值（可选，MD5）
- chunk_size: 分块大小（默认 5MB）

响应：
{
  "session_id": "uuid",
  "file_name": "example.pdf",
  "file_size": 10485760,
  "file_hash": "md5_hash",
  "chunk_size": 5242880,
  "uploaded_chunks": [],
  "total_chunks": 20
}
```

#### 2. 上传文件块

```http
POST /api/files/upload/chunk
Content-Type: multipart/form-data

参数：
- session_id: 会话 ID
- chunk_index: 块索引（0-based）
- chunk_data: 块数据（文件）
- chunk_hash: 块哈希值（可选）

响应：
{
  "status": "success",
  "chunk_index": 0,
  "uploaded_chunks": 1,
  "total_chunks": 20
}
```

#### 3. 完成上传

```http
POST /api/files/upload/complete
Content-Type: application/json

参数：
- session_id: 会话 ID

响应：
{
  "status": "completed",
  "file_path": "/path/to/file",
  "file_name": "example.pdf",
  "file_size": 10485760
}
```

#### 4. 获取上传状态

```http
GET /api/files/upload/status/{session_id}

响应：
{
  "session_id": "uuid",
  "file_name": "example.pdf",
  "file_size": 10485760,
  "uploaded_chunks": 15,
  "total_chunks": 20,
  "progress": 75.0,
  "status": "uploading"
}
```

#### 5. 取消上传

```http
DELETE /api/files/upload/{session_id}

响应：
{
  "status": "cancelled",
  "session_id": "uuid"
}
```

### 任务管理接口

#### 1. 处理知识库

```http
POST /api/files/process-knowledge-base
Content-Type: multipart/form-data

参数：
- file_path: 文件路径
- config: 配置（JSON 字符串，可选）

响应：
{
  "task_id": "celery-task-id",
  "status": "pending",
  "message": "Knowledge base processing task created"
}
```

#### 2. 获取任务状态

```http
GET /api/files/task/{task_id}

响应：
{
  "task_id": "celery-task-id",
  "status": "completed",
  "result": {
    "success": true,
    "knowledge_base": {...}
  }
}
```

#### 3. 取消任务

```http
DELETE /api/files/task/{task_id}

响应：
{
  "task_id": "celery-task-id",
  "status": "cancelled"
}
```

## 使用示例

### 断点续传示例

```python
import requests
import hashlib

# 1. 初始化上传会话
file_path = "large_file.pdf"
file_size = os.path.getsize(file_path)
file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

response = requests.post(
    "http://localhost:8000/api/files/upload/init",
    data={
        "file_name": os.path.basename(file_path),
        "file_size": file_size,
        "file_hash": file_hash,
        "chunk_size": 5 * 1024 * 1024  # 5MB
    }
)

session_info = response.json()
session_id = session_info["session_id"]

# 2. 分块上传文件
chunk_size = session_info["chunk_size"]
with open(file_path, 'rb') as f:
    for chunk_index in range(session_info["total_chunks"]):
        chunk_data = f.read(chunk_size)
        
        # 上传块
        chunk_hash = hashlib.md5(chunk_data).hexdigest()
        requests.post(
            f"http://localhost:8000/api/files/upload/chunk",
            data={
                "session_id": session_id,
                "chunk_index": chunk_index,
                "chunk_hash": chunk_hash
            },
            files={"chunk_data": ("chunk", chunk_data)}
        )
        
        print(f"Uploaded chunk {chunk_index + 1}/{session_info['total_chunks']}")

# 3. 完成上传
response = requests.post(
    f"http://localhost:8000/api/files/upload/complete",
    json={"session_id": session_id}
)

result = response.json()
file_path = result["file_path"]

# 4. 处理知识库
response = requests.post(
    "http://localhost:8000/api/files/process-knowledge-base",
    data={
        "file_path": file_path,
        "config": "{}"
    }
)

task_info = response.json()
task_id = task_info["task_id"]

# 5. 轮询任务状态
while True:
    response = requests.get(f"http://localhost:8000/api/files/task/{task_id}")
    status_info = response.json()
    
    if status_info["status"] == "completed":
        print("Task completed!")
        print("Result:", status_info["result"])
        break
    elif status_info["status"] == "failed":
        print("Task failed!")
        print("Error:", status_info["result"]["error"])
        break
    else:
        print(f"Task status: {status_info['status']}")
        time.sleep(2)
```

## 技术特点

### 1. 断点续传
- 支持大文件分块上传
- 自动检测已上传的块
- 支持断点恢复
- 文件哈希验证

### 2. 任务解耦
- 文件上传与处理任务分离
- 异步处理耗时的文档解析
- 支持任务取消和状态查询
- 任务结果持久化

### 3. 并发处理
- Celery Worker 并发处理任务
- Redis 作为消息代理
- 支持多个 Worker 实例
- 任务队列管理

### 4. 错误处理
- 完善的异常处理机制
- 任务失败重试
- 详细的错误信息
- 日志记录

## 监控和管理

### Celery 监控

```bash
# 启动 Flower（Celery 监控工具）
pip install flower
celery -A app.core.tasks.celery_config flower

# 访问监控界面
# http://localhost:5555
```

### 日志查看

```bash
# 查看 Celery Worker 日志
# 日志会输出到控制台

# 查看 FastAPI 日志
# 日志会输出到控制台
```

## 性能优化

### 1. 文件上传优化
- 可配置的分块大小
- 并发上传支持
- 哈希验证确保数据完整性
- 临时文件自动清理

### 2. 任务处理优化
- 任务超时控制
- 软超时和硬超时
- 任务优先级支持
- Worker 预取配置

### 3. 资源管理
- 内存使用控制
- 文件句柄管理
- 临时文件清理
- 连接池管理

## 故障排查

### Redis 连接问题
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查 Redis 配置
redis-cli info
```

### Celery Worker 问题
```bash
# 检查 Worker 状态
celery -A app.core.tasks.celery_config inspect active

# 查看任务队列
celery -A app.core.tasks.celery_config inspect registered
```

### 文件上传问题
```bash
# 检查临时文件目录
ls -la ./data/temp_uploads

# 检查文件权限
chmod 755 ./data/temp_uploads
```

## 部署建议

### 1. 生产环境配置
- 使用 Redis Cluster 提高可用性
- 配置 Celery Worker 自动重启
- 设置适当的任务超时
- 启用任务结果过期

### 2. 安全配置
- 配置 Redis 密码
- 启用 TLS 加密
- 限制文件上传大小
- 添加认证机制

### 3. 监控配置
- 配置日志收集
- 设置性能监控
- 配置告警机制
- 定期备份数据

## 总结

异步任务队列系统已经完全实现，包括：

✅ 基于 FastAPI 的异步 RESTful 服务
✅ 利用 Celery + Redis 实现任务队列
✅ 支持断点续传与任务状态轮询
✅ 确保系统在并发上传大文件时的稳定性
✅ 文件上传与 API 服务的解耦
✅ 耗时文档解析任务的异步处理

系统可以处理大文件上传和耗时的文档处理任务，提供了良好的用户体验和系统稳定性。