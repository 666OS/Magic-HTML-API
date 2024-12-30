# magic-html-api

一个智能的网页内容提取API服务，基于magic-html和jina-ai/reader。支持多种内容类型（文章/论坛/微信/知乎），多种输出格式（文本/Markdown/HTML）。只保留主要文章内容，使AI能够更好地理解和分析文本。

## 功能特点

- 🔍 智能识别网页类型并提取主要内容
- 📚 支持多种内容类型（文章/论坛/微信/知乎）
- 📝 多种输出格式（文本/Markdown/HTML）
- ⚡ 异步处理，响应迅速
- 🚀 部署在Vercel上，免费使用
- 🤖 自动降级处理：当默认提取失败时自动使用jina-ai/reader

## 🔗 在线演示

访问 [https://magic-html-api.vercel.app](https://magic-html-api.vercel.app) 体验在线版本。

一键部署：[![Vercel Deployment](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/eggacheb/Magic-HTML-API)


![image](https://github.com/user-attachments/assets/6ac7637c-909a-47c1-b756-9e7d93c466e3)
![image](https://github.com/user-attachments/assets/3ddacaf3-8fbe-4ab5-a306-e81fdc2a2152)
![image](https://github.com/user-attachments/assets/03637a58-6870-4101-b350-785a3f36bed3)


## API使用

### 内容提取

```
GET /api/extract
```

参数：
- `url`: 要提取内容的网页URL（必需）
- `output_format`: 输出格式（可选，默认为"text"）
  - text: 纯文本格式
  - markdown: Markdown格式
  - html: HTML格式

示例请求：
```
https://your-domain.vercel.app/api/extract?url=https://example.com&output_format=markdown
```

响应格式：
```json
{
    "url": "请求的URL",
    "content": "提取的内容",
    "format": "输出格式",
    "type": "内容类型",
    "success": true
}
```

内容类型（type）包括：
- article: 文章
- forum: 论坛
- weixin: 微信文章
- jina: AI提取（使用jina-ai/reader处理）

## 技术实现

- 使用[magic-html](https://github.com/opendatalab/magic-html)作为主要内容提取引擎
- 集成[jina-ai/reader](https://github.com/jina-ai/reader)作为备选提取方案
- 自动识别网页类型并选择最佳提取策略
- 智能降级：当默认提取失败时自动切换到jina-ai/reader

## 部署

本项目使用Vercel部署，直接导入GitHub仓库即可。

### 环境要求
- Python 3.9+
- Node.js 16+

### 部署步骤
1. Fork本仓库
2. 在Vercel中导入项目
3. 部署完成后即可使用

## 技术栈

### 后端
- FastAPI
- magic-html
- jina-ai/reader
- Python 3.9+

### 前端
- Next.js 13
- React
- Tailwind CSS
- TypeScript

### 部署
- Vercel

## 致谢

- [magic-html](https://github.com/opendatalab/magic-html) - 强大的网页内容提取库
- [jina-ai/reader](https://github.com/jina-ai/reader) - 优秀的AI内容提取服务

## License

MIT 
