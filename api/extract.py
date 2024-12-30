from fastapi import FastAPI, HTTPException
import httpx
from magic_html import GeneralExtractor
from typing import Optional, Literal
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re
import chardet

app = FastAPI()
extractor = GeneralExtractor()

# 更新默认请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}

async def fetch_url(url: str) -> str:
    async with httpx.AsyncClient(
        verify=False,
        follow_redirects=True,
        cookies={},
        timeout=30.0
    ) as client:
        try:
            response = await client.get(
                url,
                headers=DEFAULT_HEADERS
            )
            response.raise_for_status()
            
            # 处理响应编码
            content_type = response.headers.get('content-type', '').lower()
            if 'charset=' in content_type:
                try:
                    charset = content_type.split('charset=')[-1].split(';')[0]
                    return response.content.decode(charset)
                except:
                    pass
            
            try:
                return response.content.decode('utf-8')
            except UnicodeDecodeError:
                content = response.content
                detected = chardet.detect(content)
                encoding = detected['encoding']
                
                if encoding and encoding.lower() in ['gb2312', 'gbk']:
                    encoding = 'gb18030'
                
                return content.decode(encoding or 'utf-8')
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

def clean_markdown(text: str) -> str:
    """
    清理和优化markdown文本
    
    Args:
        text: 原始markdown文本
        
    Returns:
        清理后的markdown文本
    """
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 移除行首尾的空格
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # 移除不必要的标记符号
    text = re.sub(r'={3,}', '', text)
    # 优化图片链接格式
    text = re.sub(r'!\[\]\((.*?)\)', r'![图片](\1)', text)
    return text.strip()

def convert_content(html: str, output_format: str) -> str:
    """
    将HTML内容转换为指定格式
    
    Args:
        html: HTML内容
        output_format: 输出格式 ("html", "markdown", "text")
        
    Returns:
        转换后的内容
    """
    if not isinstance(html, str):
        html = str(html)
        
    if output_format == "html":
        return html
    elif output_format == "markdown":
        markdown = md(html)
        return clean_markdown(markdown)
    elif output_format == "text":
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    else:
        return html

def extract_html_content(data: dict) -> str:
    """
    从magic_html返回的数据中提取HTML内容
    
    Args:
        data: magic_html返回的数据
        
    Returns:
        HTML内容
    """
    if isinstance(data, dict):
        return data.get('html', '')
    return ''

def detect_html_type(html: str, url: str) -> str:
    """
    自动检测HTML类型
    
    Args:
        html: HTML内容
        url: 页面URL
        
    Returns:
        检测到的类型 ("article", "forum", "weixin", "jina")
    """
    # 检查URL特征
    url_lower = url.lower()
    if any(domain in url_lower for domain in ['mp.weixin.qq.com', 'weixin.qq.com']):
        return 'weixin'
    elif 'zhihu.com' in url_lower:
        return 'jina'
    
    # 检查HTML特征
    soup = BeautifulSoup(html, 'html.parser')
    
    # 论坛特征检测
    forum_indicators = [
        'forum', 'topic', 'thread', 'post', 'reply', 'comment', 'discuss',
        '论坛', '帖子', '回复', '评论', '讨论'
    ]
    
    # 检查类名和ID
    classes_and_ids = []
    for element in soup.find_all(class_=True):
        classes_and_ids.extend(element.get('class', []))
    for element in soup.find_all(id=True):
        classes_and_ids.append(element.get('id', ''))
    
    classes_and_ids = ' '.join(classes_and_ids).lower()
    
    if any(indicator in classes_and_ids for indicator in forum_indicators):
        return 'forum'
    
    # 默认为文章类型
    return 'article'

# 添加jina.ai提取函数
async def fetch_from_jina(url: str) -> str:
    """
    使用jina.ai服务提取内容
    
    Args:
        url: 目标网页URL
        
    Returns:
        提取的内容
    """
    jina_url = f"https://r.jina.ai/{url}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(jina_url)
        response.raise_for_status()
        return response.text

def convert_markdown(markdown: str, output_format: str) -> str:
    """
    将markdown内容转换为指定格式
    
    Args:
        markdown: Markdown内容
        output_format: 输出格式 ("html", "markdown", "text")
        
    Returns:
        转换后的内容
    """
    if output_format == "markdown":
        return markdown
    elif output_format == "text":
        # 移除markdown标记
        text = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', markdown)  # 替换图片
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # 替换链接
        text = re.sub(r'[#*`]', '', text)  # 移除特殊字符
        return text.strip()
    elif output_format == "html":
        # 这里可以使用markdown到html的转换库，比如markdown2或mistune
        # 暂时返回原始markdown
        return markdown
    return markdown

@app.get("/api/extract")
async def extract_content(
    url: str, 
    output_format: Optional[Literal["html", "markdown", "text"]] = "text"
):
    """
    从URL提取内容
    
    Args:
        url: 目标网页URL
        output_format: 输出格式 ("html", "markdown", "text")，默认为text
    
    Returns:
        JSON格式的提取内容
    """
    try:
        # 检测是否是知乎页面
        if 'zhihu.com' in url:
            markdown_content = await fetch_from_jina(url)
            content = convert_markdown(markdown_content, output_format)
            return {
                "url": url,
                "content": content,
                "format": output_format,
                "type": "jina",
                "success": True
            }
            
        # 尝试使用原有逻辑
        try:
            html = await fetch_url(url)
            html_type = detect_html_type(html, url)
            extracted_data = extractor.extract(html, base_url=url, html_type=html_type)
            html_content = extract_html_content(extracted_data)
            
            # 检查提取结果是否为空
            if not html_content or html_content.isspace():
                # 如果为空，尝试使用jina.ai
                markdown_content = await fetch_from_jina(url)
                content = convert_markdown(markdown_content, output_format)
                return {
                    "url": url,
                    "content": content,
                    "format": output_format,
                    "type": "jina",
                    "success": True
                }
            
            # 使用原有结果
            converted_content = convert_content(html_content, output_format)
            return {
                "url": url,
                "content": converted_content,
                "format": output_format,
                "type": html_type,
                "success": True
            }
            
        except Exception as e:
            # 如果原有逻辑失败，尝试使用jina.ai
            markdown_content = await fetch_from_jina(url)
            content = convert_markdown(markdown_content, output_format)
            return {
                "url": url,
                "content": content,
                "format": output_format,
                "type": "jina",
                "success": True
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 