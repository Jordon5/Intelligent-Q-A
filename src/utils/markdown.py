"""Markdown 处理工具"""
import re
import markdown
import frontmatter

def markdown_to_text(markdown_content: str) -> str:
    """将 Markdown 转换为纯文本"""
    # 移除 Front-Matter
    post = frontmatter.loads(markdown_content)
    content = post.content
    # 转换为 HTML
    html = markdown.markdown(content)

    # 移除 html 标签
    text = re.sub(r'<[^>]+>', '', html)

    # 清理空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_metadata(markdown_content: str) -> dict:
    """提取 Markdown 中的 front matter 元数据"""
    post = frontmatter.loads(markdown_content)
    return dict(post.metadata)

def read_markdown_file(file_path: str) -> tuple[str, dict]:
    """ 读取 Markdown 文件并返回内容和元数据"""
    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()

    text = markdown_to_text(content)
    metadata = extract_metadata(content)

    return text, metadata


