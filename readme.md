# 数字身份 RAG 聊天机器人

基于 Python 的数字身份聊天机器人，使用 RAG (Retrieval-Augmented Generation) 技术，能够根据人物知识库生成符合角色特征的对话。

## 功能特性

- **模块化设计**：低耦合度，清晰的代码结构
- **自定义人物**：支持通过配置文件定制人物身份
- **知识库管理**：结构化的人物知识存储
- **向量检索**：基于 ChromaDB 的高效向量搜索
- **LLM 集成**：支持 Qwen API 生成符合人物风格的回答
- **FastAPI 服务**：高性能的 RESTful API 接口
- **自动文档**：Swagger UI 和 ReDoc 自动生成的 API 文档

## 技术栈

- **Python 3.10+**
- **FastAPI**：现代化的 Web 框架
- **ChromaDB**：轻量级向量数据库
- **Qwen API**：阿里云通义千问大语言模型
- **Pydantic**：数据验证和设置管理
- **AsyncIO**：异步编程支持

## 项目结构
rag-chatbot-py/
├── src/                # 源代码
│   ├── api/            # API 服务层
│   ├── config.py       # 配置管理
│   ├── llm/            # LLM 抽象和实现
│   ├── rag/            # RAG 核心逻辑
│   └── vector_store/   # 向量存储抽象和实现
├── scripts/            # 脚本
│   └── ingest.py       # 数据摄入脚本
├── tests/              # 测试
│   ├── test_core.py    # 核心测试
│   └── test_rag.py     # RAG 测试
├── character-knowledge/ # 人物知识库
├── .env.example        # 环境变量示例
├── .gitignore          # Git 忽略文件
├── requirements.txt    # 依赖管理
└── README.md           # 项目文档


## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/digital-identity-rag-chatbot.git
cd digital-identity-rag-chatbot
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 填写 Qwen API 密钥和其他配置

```env
# Qwen API 配置
QWEN_API_KEY=your-qwen-api-key
QWEN_CHAT_MODEL=qwen-plus
QWEN_EMBED_MODEL=text-embedding-v4

# 向量数据库配置
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=rag_collection

# 数字分身配置
CHARACTER_NAME=齐静春
CHARACTER_ERA=骊珠洞天
CHARACTER_PERSONALITY=温润如玉，书卷气浓厚，仁义当先
CHARACTER_SPEAKING_STYLE=言语温和，引经据典，有教书先生的儒雅气质
CHARACTER_BACKGROUND=文圣弟子，曾任山崖书院山主，是{character_name}的启蒙恩师
```

### 5. 创建人物知识库

在 `character-knowledge/` 目录中创建以下结构：
character-knowledge/
├── core/
│   ├── identity.md     # 核心身份档案
│   ├── personality.md  # 性格特征画像
│   └── style.md        # 语言风格指南
├── background/
│   ├── era.md          # 时代背景
│   └── relationships.md # 人际关系图谱
└── dialogues/
├── classic-lines.md # 经典台词库
└── conversation.md  # 对话场景模拟

### 6. 数据摄入

```bash
python scripts/ingest.py
```

### 7. 启动服务

```bash
python -m src.api.main
```

## API 接口

### 聊天接口

- **URL**: `/chat`
- **方法**: POST
- **请求体**:
  ```json
  {
    "message": "你好，请介绍一下自己",
    "history": [],
    "language": "zh"
  }
  ```
- **响应**:
  ```json
  {
    "answer": "回答内容",
    "sources": [
      {
        "id": "文档ID",
        "content": "相关内容",
        "score": 相似度分数
      }
    ],
    "used_fallback": false,
    "model": "qwen-plus",
    "usage": {
      "total_tokens": 100,
      "prompt_tokens": 60,
      "completion_tokens": 40
    }
  }
  ```

### 其他接口

- **GET /**: 健康检查
- **GET /stats**: 向量库统计
- **GET /info**: 服务信息

## API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 测试

```bash
# 运行核心测试
python tests/test_core.py

# 运行 RAG 测试
python tests/test_rag.py
```

## 部署

### 本地部署

1. 按照安装步骤配置环境
2. 启动服务: `python -m src.api.main`

### 生产部署

1. 使用 Gunicorn + Uvicorn 作为生产服务器
2. 配置 Nginx 作为反向代理
3. 使用 Docker 容器化部署

## 开发指南

### 代码风格

- 遵循 PEP 8 代码风格
- 使用类型提示
- 保持模块化设计

### 扩展指南

1. **添加新的 LLM 提供商**:
   - 在 `src/llm/` 目录中创建新的实现
   - 实现 `BaseLLMProvider` 抽象基类

2. **添加新的向量存储**:
   - 在 `src/vector_store/` 目录中创建新的实现
   - 实现 `BaseVectorStore` 抽象基类

3. **添加新的人物**:
   - 在 `character-knowledge/` 目录中创建新的人物知识
   - 更新 `.env` 文件中的人物配置

