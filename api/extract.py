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
    # 配置httpx客户端
    async with httpx.AsyncClient(
        verify=False,
        follow_redirects=True,
        cookies={},  # 添加cookie支持
        timeout=30.0
    ) as client:
        try:
            # 设置referrer
            headers = DEFAULT_HEADERS.copy()
            if 'zhihu.com' in url:
                headers['referrer'] = 'https://www.zhihu.com/'
                headers['referrerPolicy'] = 'no-referrer-when-downgrade'
            
            response = await client.get(
                url,
                headers=headers
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
            
            # 尝试不同的编码方案
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
        检测到的类型 ("article", "forum", "weixin")
    """
    # 检查URL特征
    url_lower = url.lower()
    if any(domain in url_lower for domain in ['mp.weixin.qq.com', 'weixin.qq.com']):
        return 'weixin'
    
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

# 添加知乎专用的提取函数
def extract_zhihu_content(html: str, url: str) -> str:
    """
    提取知乎页面的内容
    
    Args:
        html: 页面HTML内容
        url: 页面URL
        
    Returns:
        提取的内容
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = ""
    
    # 提取问题标题
    title = None
    title_meta = soup.find('meta', {'itemprop': 'name'})
    if title_meta:
        title = title_meta.get('content')
    
    if not title:
        title_elem = soup.select_one('.QuestionHeader-title')
        if title_elem:
            title = title_elem.text.strip()
    
    if title:
        content += f"# {title}\n\n"
    
    # 提取回答内容
    answer = None
    
    # 尝试提取回答内容
    answer_item = soup.select_one('.AnswerItem, .Post-RichText, .ztext')  # 添加更多选择器
    if answer_item:
        # 提取作者信息
        author_info = answer_item.select_one('.AuthorInfo-content')
        if author_info:
            author_link = author_info.select_one('.UserLink-link')
            if author_link:
                author_name = author_link.text.strip()
                content += f"作者：{author_name}\n\n"
        
        # 提取回答正文
        answer_content = answer_item.select_one('.RichText, .RichContent-inner')  # 添加更多选择器
        if answer_content:
            # 处理数学公式
            for formula in answer_content.select('.ztext-math'):
                latex = formula.get('text', '')
                if latex:
                    formula.replace_with(f'$${latex}$$')
            
            # 处理代码块
            for code in answer_content.select('pre'):
                lang = code.get('class', [''])[0].replace('language-', '') if code.get('class') else ''
                code_text = code.text.strip()
                code.replace_with(f'\n```{lang}\n{code_text}\n```\n')
            
            # 处理行内代码
            for code in answer_content.select('code'):
                if not code.parent.name == 'pre':  # 避免重复处理代码块中的code标签
                    code.replace_with(f'`{code.text.strip()}`')
            
            # 处理表格
            for table in answer_content.select('table'):
                md_table = '\n|'
                # 处理表头
                headers = table.select('th')
                if headers:
                    md_table += '|'.join(th.text.strip() for th in headers) + '|\n|'
                    md_table += '|'.join(['---'] * len(headers)) + '|\n'
                
                # 处理表格内容
                for row in table.select('tr'):
                    cells = row.select('td')
                    if cells:
                        md_table += '|'.join(td.text.strip() for td in cells) + '|\n'
                table.replace_with(md_table)
            
            # 处理图片 (优化处理)
            for img in answer_content.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '图片')
                if src:
                    if not alt or alt == '图片':
                        # 尝试获取图片说明
                        fig_caption = img.find_next('figcaption')
                        if fig_caption:
                            alt = fig_caption.text.strip()
                    img.replace_with(f'\n![{alt}]({src})\n')
            
            # 处理链接 (优化处理)
            for a in answer_content.find_all('a'):
                href = a.get('href', '')
                if href.startswith(('http://link.zhihu.com', 'https://link.zhihu.com')):
                    try:
                        parsed = httpx.URL(href)
                        target = parsed.params.get(b'target', b'').decode('utf-8')
                        if target:
                            href = target
                    except:
                        pass
                text = a.text.strip() or href
                a.replace_with(f'[{text}]({href})')
            
            # 处理引用
            for blockquote in answer_content.select('blockquote'):
                quote_text = blockquote.get_text('\n', strip=True)
                blockquote.replace_with(f'\n> {quote_text.replace("\n", "\n> ")}\n')
            
            # 处理列表
            for ul in answer_content.select('ul'):
                for li in ul.select('li'):
                    li_text = li.get_text(strip=True)
                    li.replace_with(f'- {li_text}\n')
            
            for ol in answer_content.select('ol'):
                for i, li in enumerate(ol.select('li'), 1):
                    li_text = li.get_text(strip=True)
                    li.replace_with(f'{i}. {li_text}\n')
            
            content += answer_content.get_text('\n', strip=True)
    
    # 清理内容
    content = re.sub(r'\n{3,}', '\n\n', content)  # 移除多余的空行
    content = re.sub(r' {2,}', ' ', content)      # 移除多余的空格
    
    return content.strip()

# 修改extract_content函数，添加知乎处理
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
        html = await fetch_url(url)
        
        # 检测是否是知乎页面
        if 'zhihu.com' in url:
            # 使用知乎专用提取器
            content = extract_zhihu_content(html, url)
            # 根据需要的格式返回
            if output_format == "markdown":
                return {
                    "url": url,
                    "content": content,
                    "format": output_format,
                    "type": "zhihu",
                    "success": True
                }
            elif output_format == "text":
                # 移除markdown标记
                text = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', content)
                text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
                return {
                    "url": url,
                    "content": text,
                    "format": output_format,
                    "type": "zhihu",
                    "success": True
                }
        
        # 非知乎页面使用原有逻辑
        html_type = detect_html_type(html, url)
        extracted_data = extractor.extract(html, base_url=url, html_type=html_type)
        html_content = extract_html_content(extracted_data)
        converted_content = convert_content(html_content, output_format)
        
        return {
            "url": url,
            "content": converted_content,
            "format": output_format,
            "type": html_type,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 