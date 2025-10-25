#!/bin/bash
# Hugo專用自動更新腳本

echo "🚀 開始Hugo AI選股資料更新..."
cd ~/my-website

# 備份當前資料
cp static/data/stock-data.json static/data/stock-data-backup.json

# 執行Python更新腳本
python3 hugo_stock_updater.py

# 可選: 自動重啟Hugo伺服器
# pkill hugo
# hugo server -D &

echo "✅ Hugo資料更新完成！"
echo "📊 請訪問: http://localhost:1313 查看更新結果"
