#!/bin/bash
set -e  # 遇到错误立即退出
echo "Starting build process..."

# 更新pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# 安装基本依赖
echo "Installing base dependencies..."
pip install fastapi==0.104.1 httpx==0.25.2 uvicorn==0.24.0

# 安装magic-html
echo "Installing magic-html..."
pip install --no-cache-dir https://github.com/opendatalab/magic-html/releases/download/magic_html-0.1.2-released/magic_html-0.1.2-py3-none-any.whl

echo "Build process completed."