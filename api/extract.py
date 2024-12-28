from fastapi import FastAPI, HTTPException
import httpx
from magic_html import GeneralExtractor
from typing import Optional
import json

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

@app.get("/api/extract")
async def extract_content(url: str, html_type: Optional[str] = "article"):
    """
    Extract content from URL using magic-html
    
    Args:
        url: Target webpage URL
        html_type: Type of HTML content ("article", "forum", "weixin")
    
    Returns:
        JSON with extracted content
    """
    try:
        html = await fetch_url(url)
        data = extractor.extract(html, base_url=url, html_type=html_type)
        
        return {
            "url": url,
            "content": data,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to magic-html extractor API"} 