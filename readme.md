# 万能问答框架

基于 RAG 技术的智能问答框架，支持用户上传知识库并生成专属的问答助手。

## 功能特点

- **多种文件格式支持**：支持 Markdown、PDF、Word、TXT、JSON 等多种文件格式
- **高级 PDF 解析**：支持多栏排版、表格提取、图片识别等复杂 PDF 处理
- **混合检索策略**：BM25 关键词检索 + Dense Vector 语义检索 + 倒数排名融合
- **父子索引分块**：小区块保证检索精度，大区块提供完整上下文
- **异步任务队列**：基于 Celery + Redis 的异步任务处理，支持断点续传
- **自动知识库处理**：自动解析文档并创建向量存储
- **一键创建助手**：基于知识库快速创建专属问答助手
- **智能问答**：基于 RAG 技术的智能问答，支持 ReAct 推理流程
- **任务管理**：后台处理知识库任务，实时监控任务状态
- **完整的 API**：提供全面的 RESTful API 接口
- **友好的界面**：直观的 Web 界面，操作简单

## 技术栈

- **后端**：Python 3.8+、FastAPI、ChromaDB
- **异步任务**：Celery、Redis
- **前端**：HTML、CSS、JavaScript、Bootstrap
- **文档处理**：PyPDF2、python-docx、markdown、PyMuPDF、Camelot
- **配置管理**：Pydantic、PyYAML
- **任务调度**：Celery + Redis
- **API 文档**：Swagger UI

## 核心优化

### 1. ETL 流水线设计
- **基于布局分析的文档解析模块**：使用 PyMuPDF 进行文档版面分析，通过坐标排序算法解决多栏排版错乱问题
- **表格数据结构化提取**：针对表格数据，开发了基于 Markdown 的结构化提取
- **图片多模态描述**：引入多模态模型对文档图片生成描述性文本

### 2. 混合检索策略
- **BM25 关键词检索**：对专有名词有精确匹配效果
- **Dense Vector 语义检索**：对语义相关内容有良好理解
- **倒数排名融合算法**：对双路召回结果进行加权排序
- **混合检索**：显著提升专有名词和长尾问题的检索准确率

### 3. 父子索引分块策略
- **小区块保证检索精度**：子块较小（600字符），更容易与查询匹配
- **大区块提供完整上下文**：父块较大（2000字符），提供完整信息
- **ID 关联实现父子映射**：通过唯一 ID 实现父子块的映射
- **有效提升 LLM 回答连贯性**：避免长文档被切分成不相关的小块

### 4. 异步任务队列系统
- **基于 FastAPI 的异步 RESTful 服务**：异步处理 HTTP 请求，快速响应
- **利用 Celery + Redis 实现任务队列**：解耦文件上传与处理任务
- **支持断点续传与任务状态轮询**：大文件分块上传，实时状态查询
- **确保系统在并发上传大文件时的稳定性**：并发处理机制，资源限制控制

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- Redis 服务器（用于异步任务队列）

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd rag-chatbot-py
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件，添加以下内容：

```env
# Qwen API 配置
QWEN_API_KEY=your-qwen-api-key
QWEN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 向量存储配置
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIR=./data/vector

# 知识库配置
KNOWLEDGE_BASE_DIR=./data/knowledge

# 任务配置
TASK_DIR=./data/tasks

# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 文件上传配置
MAX_FILE_SIZE=104857600  # 100MB
CHUNK_SIZE=5242880  # 5MB
```

4. **激活环境**

在启动服务前，确保已激活 `rag_env` 环境：

```powershell
# 激活环境
conda activate rag_env

# 验证环境
python check_env.py
```

**注意**：如果遇到 `ModuleNotFoundError`，说明当前不在正确的环境中。

5. **启动服务**

### 方案 A：开发环境（无需安装 Redis）

项目集成了 `fakeredis`，无需安装 Redis 即可开发和测试。

```bash
# Windows PowerShell
$env:DEV_MODE="true"
python start_api_server.py

# Windows CMD
set DEV_MODE=true
python start_api_server.py

# Linux/Mac
DEV_MODE=true python start_api_server.py
```

### 方案 B：生产环境（需要 Redis）

#### 启动 Redis

```bash
# Windows（需先安装 Redis）
redis-server

# Linux/Mac
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 --name redis redis
```

#### 启动 Celery Worker

```bash
python start_celery_worker.py
```

#### 启动后端服务

```bash
python start_api_server.py
```

**注意**：如果在 Windows 上遇到 `redis-server` 命令未找到，是因为 Redis 没有添加到系统 PATH。可以使用以下方式：

#### 方式 1：使用一键启动脚本（推荐）
```powershell
# 一键启动所有服务（Redis + Celery Worker + API Server）
.\start_all.ps1

# 开发模式（无需 Redis）
.\start_all.ps1 -DevMode

# 跳过 Redis（如果已启动）
.\start_all.ps1 -SkipRedis

# 跳过 Celery Worker
.\start_all.ps1 -SkipWorker
```

#### 方式 2：手动启动 Redis
```powershell
# 使用脚本启动 Redis
.\start_redis.ps1

# 或使用完整路径
"C:\Program Files\Redis\redis-server.exe" "C:\Program Files\Redis\redis.windows.conf"
```

#### 方式 3：添加 Redis 到系统 PATH
1. 打开系统环境变量设置
2. 找到 Path 变量，添加 `C:\Program Files\Redis`
3. 重启终端，然后可以直接使用 `redis-server`

更多详情参考 [DEV_SETUP.md](DEV_SETUP.md)

### 传统启动方式

- **Windows**：`./start.ps1`
- **Linux/Mac**：`./start.sh`

### 启动前端服务

前端服务已经集成在后端服务中，当后端服务启动后，前端页面会自动通过以下地址访问：

- Web 界面：http://localhost:8000

5. **访问地址**

- API 文档：http://localhost:8000/docs

### 运行测试

项目提供了完整的测试套件，可以验证各个功能模块是否正常工作。

**运行所有测试：**
```bash
python run_tests.py
```

**运行指定测试：**
```bash
# 异步任务队列测试
python run_tests.py async

# 混合检索测试
python run_tests.py hybrid

# 父子分块测试
python run_tests.py chunk

# 长文本分块测试
python run_tests.py long_text

# 完整父子分块流程测试
python run_tests.py complete

# 验证父子分块实现
python run_tests.py verify
```

**直接运行单个测试文件：**
```bash
python -m tests.test_async_task_system
python -m tests.test_hybrid_search
python -m tests.test_parent_child_chunking
```

## 使用指南

### 1. 上传知识库

1. 进入 **知识库管理** 页面
2. 填写知识库名称和描述
3. 上传文档文件（支持 Markdown、PDF、Word、TXT、JSON 等多种格式）
4. 点击 **上传并处理** 按钮
5. 等待任务处理完成（可在任务管理页面查看进度）

**大文件上传支持**：
- 支持断点续传，上传中断后可恢复
- 文件分块上传，提高上传稳定性
- 实时上传进度显示

### 2. 创建助手

1. 进入 **助手管理** 页面
2. 填写助手名称和描述
3. 选择一个已处理完成的知识库
4. 点击 **创建助手** 按钮

### 3. 与助手聊天

1. 进入 **聊天** 页面
2. 选择一个已创建的助手
3. 在输入框中输入问题
4. 点击 **发送** 按钮或按 Enter 键
5. 等待助手回答

### 4. 管理任务

1. 进入 **任务管理** 页面
2. 查看任务列表和状态
3. 可以取消正在执行的任务
4. 查看任务详细信息和结果

## API 接口

### 知识库管理

- `POST /api/knowledge-bases/validate` - 验证知识库格式
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases` - 列出所有知识库
- `GET /api/knowledge-bases/{kb_id}` - 获取知识库信息
- `DELETE /api/knowledge-bases/{kb_id}` - 删除知识库

### 文件上传（断点续传）

- `POST /api/files/upload/init` - 初始化上传会话
- `POST /api/files/upload/chunk` - 上传文件块
- `POST /api/files/upload/complete` - 完成上传
- `GET /api/files/upload/status/{session_id}` - 获取上传状态
- `DELETE /api/files/upload/{session_id}` - 取消上传

### 异步任务管理

- `POST /api/files/process-knowledge-base` - 处理知识库（异步任务）
- `GET /api/files/task/{task_id}` - 获取任务状态
- `DELETE /api/files/task/{task_id}` - 取消任务

### 传统任务管理

- `GET /api/tasks` - 列出任务
- `GET /api/tasks/{task_id}` - 获取任务状态
- `POST /api/tasks/{task_id}/cancel` - 取消任务

### 助手管理

- `POST /api/assistants` - 创建助手
- `GET /api/assistants` - 列出所有助手
- `GET /api/assistants/{assistant_id}` - 获取助手信息
- `DELETE /api/assistants/{assistant_id}` - 删除助手
- `POST /api/assistants/{assistant_id}/chat` - 与助手聊天

### 系统接口

- `GET /` - 根路径
- `GET /health` - 健康检查

## 项目结构

```
rag-chatbot-py/
├── app/                          # 应用程序主目录
│   ├── api/                      # API 服务模块
│   │   ├── __init__.py
│   │   ├── main.py               # 主 API 服务入口
│   │   └── file_upload_fixed.py  # 文件上传和断点续传 API
│   ├── core/                     # 核心功能模块
│   │   ├── config/               # 配置管理
│   │   │   ├── __init__.py
│   │   │   └── manager.py
│   │   ├── knowledge/            # 知识库管理
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # 知识库管理器
│   │   │   ├── parser.py         # 文档解析器（支持多种格式）
│   │   │   ├── parent_child_chunker.py    # 父子索引分块器
│   │   │   └── parent_child_retriever.py  # 父子块检索器
│   │   ├── task/                 # 任务调度（传统）
│   │   │   ├── __init__.py
│   │   │   └── scheduler.py
│   │   ├── tasks/                # Celery 异步任务
│   │   │   ├── celery_config.py  # Celery 配置
│   │   │   └── celery_tasks.py   # Celery 任务定义
│   │   └── vector/               # 向量存储
│   │       ├── __init__.py
│   │       └── store.py          # 向量存储管理器（含混合检索）
│   └── ui/                       # 用户界面
│       └── static/
│           └── index.html
├── data/                         # 数据存储目录
│   ├── knowledge/                # 知识库数据
│   ├── vector/                   # 向量存储数据
│   ├── tasks/                    # 任务数据
│   └── temp_uploads/             # 临时上传文件
├── scripts/                      # 脚本工具
│   └── ingest.py
├── tests/                        # 测试代码
│   ├── test_async_task_system.py           # 异步任务队列测试
│   ├── test_hybrid_search.py               # 混合检索测试
│   ├── test_parent_child_chunking.py       # 父子分块测试
│   ├── test_parent_child_chunking_simple.py
│   ├── test_long_text_chunking.py          # 长文本分块测试
│   ├── test_complete_parent_child.py       # 完整父子分块流程测试
│   ├── test_pdf_parser.py                  # PDF 解析器测试
│   ├── test_pdf_parser_advanced.py
│   ├── test_pdf_parser_basic.py
│   ├── test_pdf_parser_simple.py
│   ├── test_pdf_parsing_complete.py
│   ├── test_manager_import.py
│   └── verify_parent_child_implementation.py
├── test_documents/               # 测试文档
│   └── sample.pdf
├── .env.example                  # 环境配置示例
├── .gitignore
├── readme.md                     # 项目说明
├── requirements.txt              # 依赖文件
├── run_tests.py                  # 测试运行脚本
├── start.sh                      # Linux/Mac 启动脚本
├── start.ps1                     # Windows 启动脚本
├── start_api_server.py           # API 服务启动脚本
├── start_celery_worker.py        # Celery Worker 启动脚本
├── ARCHITECTURE.md               # 架构文档
├── ASYNC_TASK_SYSTEM.md          # 异步任务系统文档
└── ASYNC_TASK_SYSTEM_SUMMARY.md  # 异步任务系统总结
```

## 技术亮点

### 1. 混合检索
结合 BM25 关键词检索和 Dense Vector 语义检索，通过倒数排名融合算法显著提升检索准确率，特别擅长处理专有名词和长尾问题。

### 2. 父子索引分块
针对长文档问答中上下文丢失的问题，实现了父子索引分块策略。在索引阶段使用小区块保证检索精度，在生成阶段通过 ID 关联召回父级大区块，有效提升了 LLM 回答的连贯性和完整性。

### 3. 异步任务队列
基于 FastAPI + Celery + Redis 的异步任务队列系统，支持断点续传与任务状态轮询，确保系统在并发上传大文件时的稳定性，实现了文件上传与 API 服务的解耦。

### 4. 高级 PDF 解析
使用 PyMuPDF 进行文档版面分析，通过坐标排序算法解决多栏排版错乱问题。针对表格数据，开发了基于 Markdown 的结构化提取。引入多模态模型对文档图片生成描述性文本。

## 性能优化

### 文件上传优化
- 可配置的分块大小（默认 5MB）
- 并发上传支持
- 哈希验证确保数据完整性
- 临时文件自动清理

### 任务处理优化
- 任务超时控制（1小时硬超时，50分钟软超时）
- Worker 预取配置（prefetch_multiplier=1）
- 任务结果过期设置
- Worker 自动重启

### 检索优化
- 混合检索策略（BM25 + Vector）
- 倒数排名融合算法
- 父子索引分块
- 缓存机制

## 常见问题

### 标签页切换不工作
- **问题**：点击导航栏中的标签页按钮没有反应
- **解决方案**：系统已内置手动标签页切换逻辑，确保浏览器缓存已清除，重新加载页面即可

### 上传文件失败
- **问题**：上传知识库文件时失败
- **解决方案**：
  - 确保文件大小不超过 100MB
  - 检查 Redis 服务是否启动
  - 检查网络连接正常
  - 尝试刷新页面后重新上传
  - 使用断点续传功能

### 助手创建失败
- **问题**：创建助手时失败
- **解决方案**：确保选择了已处理完成的知识库，检查网络连接，尝试重新创建

### 聊天无响应
- **问题**：与助手聊天时无响应
- **解决方案**：确保选择了正确的助手，检查网络连接，尝试刷新页面后重新聊天

### Celery Worker 启动失败
- **问题**：Celery Worker 无法启动
- **解决方案**：
  - 检查 Redis 服务是否运行
  - 检查 Redis 配置是否正确
  - 查看 Celery 日志获取详细错误信息

## 未来扩展

- **多模型支持**：集成更多 LLM 模型，如 GPT-4、Claude 等
- **多语言支持**：添加多语言处理能力
- **高级检索**：实现更复杂的检索策略，如混合检索
- **模型微调**：支持基于知识库的模型微调
- **部署优化**：支持容器化部署和云服务集成
- **用户认证**：添加用户认证和权限管理
- **监控系统**：添加系统监控和日志分析
- **批量处理**：支持批量知识库处理和助手创建

## 注意事项

- 上传的文档大小建议不超过 100MB
- 知识库处理时间取决于文档大小和数量
- 确保 Redis 服务已启动，以便使用异步任务队列
- 确保网络连接正常，以便与 API 服务通信
- 定期清理不需要的知识库和助手，以节省存储空间
- 生产环境建议配置 Redis 密码和 TLS 加密

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

MIT License
