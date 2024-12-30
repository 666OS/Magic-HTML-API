'use client';

import { useState } from 'react';
import { ArrowRight, Copy, Check, Github, MessageSquare, Volume2 } from 'lucide-react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [htmlType, setHtmlType] = useState('article');
  const [outputFormat, setOutputFormat] = useState('text');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleExtract = async () => {
    try {
      setLoading(true);
      setError('');
      setResult(null);

      const response = await fetch(`/api/extract?url=${encodeURIComponent(url)}&html_type=${htmlType}&output_format=${outputFormat}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '提取内容失败');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (result?.content) {
      await navigator.clipboard.writeText(result.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* 导航栏 */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-blue-100 fixed top-0 w-full z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-200">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
                Web Extractor
              </span>
            </div>
            <div className="flex items-center gap-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">功能</a>
              <a href="#api" className="text-gray-600 hover:text-blue-600 transition-colors">API</a>
              <a
                href="https://github.com/eggacheb/web-content-extractor"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="pt-28 pb-16">
        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h1 className="text-5xl font-bold text-gray-900 mb-6 bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
              智能网页内容提取
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              使用智能算法提取网页的核心内容，支持文章、论坛和微信等多种类型，
              让内容获取更加便捷。
            </p>
          </div>

          {/* 功能卡片 */}
          <div className="grid md:grid-cols-2 gap-8 mb-20" id="features">
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-blue-50 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
                <MessageSquare className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-900">智能内容提取</h3>
              <p className="text-gray-600">
                自动识别网页主要内容，支持文章、论坛和微信等多种类型，
                智能去除干扰元素。
              </p>
            </div>
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-blue-50 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
                <Volume2 className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-900">多格式支持</h3>
              <p className="text-gray-600">
                支持输出为纯文本、Markdown和HTML等多种格式，
                满足不同场景需求。
              </p>
            </div>
          </div>

          {/* 输入部分 */}
          <div className="max-w-3xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg border border-blue-50 p-8 mb-8">
              <div className="space-y-4">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="输入网页URL，例如: https://example.com"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-900 placeholder-gray-400"
                />
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">内容类型</label>
                    <select
                      value={htmlType}
                      onChange={(e) => setHtmlType(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-900"
                    >
                      <option value="article">文章</option>
                      <option value="forum">论坛</option>
                      <option value="weixin">微信</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">输出格式</label>
                    <select
                      value={outputFormat}
                      onChange={(e) => setOutputFormat(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-900"
                    >
                      <option value="text">纯文本</option>
                      <option value="markdown">Markdown</option>
                      <option value="html">HTML</option>
                    </select>
                  </div>
                </div>
                
                <button
                  onClick={handleExtract}
                  disabled={loading || !url}
                  className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl hover:from-blue-700 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-300 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 font-medium shadow-lg shadow-blue-200 hover:shadow-xl disabled:shadow-none"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      开始提取
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>

              {/* API使用说明 */}
              <div className="mt-8 pt-8 border-t border-gray-100" id="api">
                <h4 className="text-sm font-medium text-gray-900 mb-3">API 快速上手</h4>
                <div className="bg-gray-50 p-4 rounded-xl flex items-center gap-3 font-mono text-sm border border-gray-100">
                  <span className="flex-1 overflow-x-auto whitespace-nowrap text-gray-600">
                    GET /api/extract?url=https://example.com&html_type=article&output_format=text
                  </span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText('/api/extract?url=https://example.com&html_type=article&output_format=text');
                    }}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="mb-8 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm animate-shake">
                {error}
              </div>
            )}

            {/* 结果展示 */}
            {result && (
              <div className="bg-white rounded-2xl shadow-lg border border-blue-50 p-8 space-y-6">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-xl font-semibold text-gray-900">提取结果</h3>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-blue-600 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4" />
                        已复制
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        复制内容
                      </>
                    )}
                  </button>
                </div>
                <div className={`prose prose-gray max-w-none ${outputFormat === 'html' ? 'whitespace-pre-wrap font-mono text-sm' : ''}`}>
                  {result.content}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
