#!/bin/bash

echo "🧹 開始清理 GitHub 倉庫..."

# 保留的重要目錄和文件
KEEP=(
    "docs/"
    "web/"
    "README.md"
    ".gitignore"
    "index.html"
)

# 刪除不必要的文件
echo "刪除不必要的文件..."

# 刪除備份文件
find . -name "*.bak" -type f -delete
find . -name "*.backup*" -type f -delete
find . -name "*~" -type f -delete
find . -name "*.old" -type f -delete

# 刪除重複的 HTML 文件（保留 docs/web/ 和 web/ 下的）
find . -maxdepth 1 -name "*.html" -not -path "./index.html" -delete

# 刪除臨時 Python 文件
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 刪除日誌文件
find . -name "*.log" -delete

echo "✅ 清理完成！"
echo ""
echo "📁 現在的目錄結構："
ls -la
