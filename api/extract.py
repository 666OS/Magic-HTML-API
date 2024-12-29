from fastapi import FastAPI, HTTPException
import httpx
from magic_html import GeneralExtractor
from typing import Optional, Literal
import json
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re

app = FastAPI()
extractor = GeneralExtractor()

async def fetch_url(url: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
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

@app.get("/api/extract")
async def extract_content(
    url: str, 
    html_type: Optional[str] = "article",
    output_format: Optional[Literal["html", "markdown", "text"]] = "text"
):
    """
    从URL提取内容
    
    Args:
        url: 目标网页URL
        html_type: HTML内容类型 ("article", "forum", "weixin")
        output_format: 输出格式 ("html", "markdown", "text")，默认为text
    
    Returns:
        JSON格式的提取内容
    """
    try:
        html = await fetch_url(url)
        extracted_data = extractor.extract(html, base_url=url, html_type=html_type)
        
        # 从返回数据中提取HTML内容
        html_content = extract_html_content(extracted_data)
        
        # 转换内容格式
        converted_content = convert_content(html_content, output_format)
        
        return {
            "url": url,
            "content": converted_content,
            "format": output_format,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to magic-html extractor API"} 