# GitHub 推送指南

## 准备工作

### 1. 检查项目文件

确保以下敏感文件不会被提交：
- ✅ `.env` - 环境变量（已在 .gitignore）
- ✅ `data/` - 数据目录（已在 .gitignore）
- ✅ `character-knowledge/` - 知识库（已在 .gitignore）
- ✅ API keys 都从环境变量读取，无硬编码

### 2. 检查项目结构

```
rag-chatbot-py/
├── app/                      # 应用代码
│   ├── api/                  # API 服务
│   ├── core/                 # 核心功能
│   └── ui/                   # 用户界面
├── tests/                    # 测试代码
├── scripts/                  # 脚本工具
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略文件
├── LICENSE                   # MIT 许可证
├── README.md                 # 项目说明
└── requirements.txt          # 依赖列表
```

## 推送步骤

### 方式一：推送到新的 GitHub 仓库

#### 1. 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `universal-qa-framework`（或您喜欢的名称）
   - Description: `基于 RAG 的万能问答框架 - 支持多种文档格式、混合检索、父子索引分块`
   - 选择 Public 或 Private
   - **不要**勾选 "Add a README file"（我们已有）
   - **不要**勾选 "Add .gitignore"（我们已有）
   - License: MIT（我们已有）
3. 点击 "Create repository"

#### 2. 初始化本地 Git 仓库

```powershell
# 进入项目目录
cd "d:\Python Project\rag-chatbot-py"

# 初始化 Git
git init

# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 创建首次提交
git commit -m "Initial commit: Universal Q&A Framework

Features:
- Multi-format document parsing (PDF, Word, Markdown, TXT, JSON)
- Hybrid retrieval (BM25 + Dense Vector)
- Parent-child indexing for long documents
- Asynchronous task queue (Celery + Redis)
- Resumable file uploads
- FastAPI RESTful API
- Modern web UI
"
```

#### 3. 连接到 GitHub 远程仓库

```powershell
# 添加远程仓库（替换 YOUR_USERNAME 和 YOUR_REPO）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 方式二：使用 GitHub CLI（推荐）

如果您安装了 GitHub CLI (`gh`)，可以更简单：

```powershell
# 进入项目目录
cd "d:\Python Project\rag-chatbot-py"

# 初始化 Git
git init

# 添加所有文件
git add .

# 创建首次提交
git commit -m "Initial commit: Universal Q&A Framework"

# 使用 GitHub CLI 创建仓库并推送
gh repo create universal-qa-framework --public --source=. --remote=origin --push
```

## 推送后检查

### 1. 验证文件

访问您的 GitHub 仓库，确认：
- ✅ README.md 正常显示
- ✅ 没有提交 .env 文件
- ✅ 没有提交 data/ 目录
- ✅ 没有提交 API keys

### 2. 添加仓库描述

在 GitHub 仓库页面：
1. 点击 "About" 旁边的设置图标
2. 添加描述：`基于 RAG 的万能问答框架 | FastAPI + Celery + Redis + ChromaDB`
3. 添加标签：`python`, `fastapi`, `rag`, `qa-system`, `chromadb`, `celery`
4. 勾选 "Website" 并添加演示地址（如果有）

### 3. 创建 Release

```powershell
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"

# 推送标签
git push origin v1.0.0
```

然后在 GitHub 上创建 Release：
1. 访问仓库的 "Releases" 页面
2. 点击 "Draft a new release"
3. 选择标签 v1.0.0
4. 填写 Release 标题和说明

## 后续维护

### 更新代码

```powershell
# 查看修改
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "feat: 添加新功能"

# 推送到 GitHub
git push
```

### 分支管理

```powershell
# 创建新分支
git checkout -b feature/new-feature

# 在新分支上工作
git add .
git commit -m "feat: 新功能开发"

# 推送新分支
git push origin feature/new-feature

# 在 GitHub 上创建 Pull Request
gh pr create --title "新功能" --body "功能描述"
```

## 常见问题

### Q: 如何撤销错误的提交？

```powershell
# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1
```

### Q: 如何删除已提交的敏感文件？

```powershell
# 从 Git 历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

### Q: 如何更新 .gitignore？

```powershell
# 清除 Git 缓存
git rm -r --cached .

# 重新添加文件
git add .

# 提交
git commit -m "chore: 更新 .gitignore"
```

## 项目亮点（用于简历）

在推送到 GitHub 后，可以在简历中这样描述：

**万能问答框架 | Python, FastAPI, RAG**
- 基于 RAG 架构构建通用问答系统，支持 PDF、Word、Markdown 等多种文档格式
- 实现混合检索策略（BM25 + Dense Vector），通过倒数排名融合提升检索准确率
- 设计父子索引分块策略，解决长文档问答中的上下文丢失问题
- 基于 FastAPI + Celery + Redis 构建异步任务队列，支持断点续传和任务状态轮询
- 使用 PyMuPDF 进行文档版面分析，解决多栏排版、表格提取等复杂场景

## GitHub 仓库地址

推送完成后，您的仓库地址将是：
```
https://github.com/YOUR_USERNAME/universal-qa-framework
```

替换 `YOUR_USERNAME` 为您的 GitHub 用户名。
