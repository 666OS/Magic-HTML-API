# Magic HTML API

一个基于magic-html的网页内容提取API服务。

## 功能特点

- 支持从任意URL提取主要内容
- 支持多种内容类型（文章/论坛/微信）
- 异步处理，响应迅速
- 部署在Vercel上，免费使用

## API使用

### 内容提取

```
GET /api/extract
```

参数：
- `url`: 要提取内容的网页URL（必需）
- `html_type`: 内容类型（可选，默认为"article"）
  - article: 文章类型
  - forum: 论坛类型
  - weixin: 微信文章

示例请求：
```
https://your-domain.vercel.app/api/extract?url=https://example.com&html_type=article
```

响应格式：
```json
{
    "url": "请求的URL",
    "content": {
        // 提取的内容
    },
    "success": true
}
```

## 部署

本项目使用Vercel部署，直接导入GitHub仓库即可。

## 技术栈

- FastAPI
- magic-html
- Python 3.9+
- Vercel 