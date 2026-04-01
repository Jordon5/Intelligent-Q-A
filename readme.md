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
- Redis 服务器（可选，生产环境需要）

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd rag-chatbot-py
```

2. **创建虚拟环境**

```bash
# 使用 conda
conda create -n rag_env python=3.10
conda activate rag_env

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加必要的配置：
```env
# Qwen API 配置
QWEN_API_KEY=your-qwen-api-key
QWEN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Redis 配置（生产环境需要）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

5. **验证环境**

```bash
python check_env.py
```

### 启动服务

#### 方式一：开发模式

使用 fakeredis 模拟：

```bash
python start.py --dev
```

#### 方式二：生产模式

需要先安装并启动 Redis：

```bash
# 安装 Redis（Windows）
# 下载：https://github.com/microsoftarchive/redis/releases

# 启动 Redis
python start.py --redis

# 在另一个终端启动 API 服务
python start.py
```

#### 方式三：启动所有服务

```bash
# 生产模式（需要 Redis）
python start.py --all

# 开发模式（无需 Redis）
python start.py --all --dev
```

#### 方式四：单独启动服务

```bash
# 启动 Redis
python start.py --redis

# 启动 Celery Worker
python start.py --worker

# 启动 API 服务
python start.py
```

### 访问服务

启动成功后，访问以下地址：

- **Web 界面**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行指定测试
python run_tests.py async      # 异步任务测试
python run_tests.py hybrid     # 混合检索测试
python run_tests.py chunk      # 父子分块测试
python run_tests.py pdf        # PDF 解析测试
```

## 项目结构

```
rag-chatbot-py/
├── app/                          # 应用程序主目录
│   ├── api/                      # API 服务模块
│   │   ├── main.py               # 主 API 服务入口
│   │   └── file_upload_fixed.py  # 文件上传和断点续传 API
│   ├── core/                     # 核心功能模块
│   │   ├── config/               # 配置管理
│   │   ├── knowledge/            # 知识库管理
│   │   │   ├── manager.py        # 知识库管理器
│   │   │   ├── parser.py         # 文档解析器
│   │   │   ├── parent_child_chunker.py    # 父子索引分块器
│   │   │   └── parent_child_retriever.py  # 父子块检索器
│   │   ├── tasks/                # Celery 异步任务
│   │   │   ├── celery_config.py  # Celery 配置
│   │   │   └── celery_tasks.py   # Celery 任务定义
│   │   └── vector/               # 向量存储
│   │       └── store.py          # 向量存储管理器（含混合检索）
│   └── ui/                       # 用户界面
│       └── static/
│           └── index.html
├── tests/                        # 测试代码
│   ├── test_async_task_system.py           # 异步任务队列测试
│   ├── test_hybrid_search.py               # 混合检索测试
│   ├── test_parent_child_chunking.py       # 父子分块测试
│   ├── test_long_text_chunking.py          # 长文本分块测试
│   ├── test_complete_parent_child.py       # 完整父子分块流程测试
│   ├── test_pdf_parser.py                  # PDF 解析器测试
│   └── verify_parent_child_implementation.py
├── scripts/                      # 脚本工具
│   └── ingest.py
├── test_documents/               # 测试文档
│   └── sample.pdf
├── .env.example                  # 环境配置示例
├── .gitignore
├── LICENSE                       # MIT 许可证
├── README.md                     # 项目说明
├── requirements.txt              # 依赖文件
├── start.py                      # 统一启动脚本
├── run_tests.py                  # 测试运行脚本
├── check_env.py                  # 环境检查脚本
└── start_celery_worker.py        # Celery Worker 启动脚本
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

## API 文档

启动服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要接口

- `POST /api/knowledge-bases/validate` - 验证知识库格式
- `POST /api/knowledge-bases/create` - 创建知识库
- `POST /api/assistants/create` - 创建助手
- `POST /api/chat` - 与助手聊天
- `GET /api/tasks/{task_id}` - 查询任务状态

## 常见问题

### Q: 如何切换开发模式和生产模式？
A: 使用 `python start.py --dev` 启动开发模式（fakeredis），使用 `python start.py` 启动生产模式（需要 Redis）。

### Q: Redis 连接失败怎么办？
A: 
1. 检查 Redis 是否启动：`python start.py --redis`
2. 或使用开发模式：`python start.py --dev`

### Q: 如何添加新的文档格式支持？
A: 在 `app/core/knowledge/parser.py` 中添加新的解析方法。

### Q: 如何自定义分块策略？
A: 修改 `app/core/knowledge/parent_child_chunker.py` 中的分块参数。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请提交 Issue。

---

**如果这个项目对您有帮助，请给一个 ⭐️ Star！**
