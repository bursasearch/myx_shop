#!/bin/bash
echo "🚀 启动 BursaSearch..."
echo "📂 目录: $(pwd)"
echo "🌐 访问: http://127.0.0.1:5000/admin/shopee_dashboard.html"
python3 -m http.server 5000
