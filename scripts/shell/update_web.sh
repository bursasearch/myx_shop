#!/bin/bash
echo "🌐 更新網站文件到正確位置..."
echo "=============================="

# 設置正確的路徑
WEB_DIR="/storage/emulated/0/bursasearch/myx_shop/web"
SCRIPTS_DIR="$(pwd)"
DATA_SOURCE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"

echo "📅 開始時間: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 查找最新數據
LATEST_CSV=$(ls -t "$DATA_SOURCE"/*.csv 2>/dev/null | head -1)
if [ -z "$LATEST_CSV" ]; then
    echo "❌ 找不到CSV文件"
    exit 1
fi

echo "📊 使用數據: $(basename "$LATEST_CSV")"

# 2. 運行AI分析
echo "🤖 運行AI分析..."
python3 ai_stock_picker.py "$LATEST_CSV"

if [ $? -ne 0 ]; then
    echo "❌ AI分析失敗"
    exit 1
fi

# 3. 更新web目錄
echo "📁 更新web目錄..."
mkdir -p "$WEB_DIR"
cp data/*.json data/*.html "$WEB_DIR/" 2>/dev/null

# 4. 更新index.html
cat > "$WEB_DIR/index.html" << HTML_EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI選股分析系統</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #4a6fa5; color: white; padding: 30px; border-radius: 10px; }
        .btn { 
            display: inline-block; 
            background: #28a745; 
            color: white; 
            padding: 12px 24px; 
            margin: 10px 5px; 
            text-decoration: none; 
            border-radius: 5px;
            font-size: 16px;
        }
        .file-list { margin: 30px 0; }
        .file-item { 
            background: #f8f9fa; 
            border-left: 4px solid #4a6fa5; 
            padding: 15px; 
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI選股分析系統</h1>
        <p>📍 正確路徑: myx_shop/web/</p>
        <p>🕐 最後更新: $(date '+%Y-%m-%d %H:%M:%S')</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="ai_analysis_preview.html" class="btn">📊 查看完整報告</a>
        <a href="picks.json" class="btn">📋 下載JSON數據</a>
        <a href="backtest_report.json" class="btn">📈 查看回測報告</a>
    </div>
    
    <div class="file-list">
        <h2>📁 文件列表</h2>
        <div class="file-item">
            <strong>ai_analysis_preview.html</strong><br>
            <small>完整HTML圖形報告，包含Top 10推薦股票</small>
        </div>
        <div class="file-item">
            <strong>picks.json</strong><br>
            <small>AI選股推薦數據，可用於網站API</small>
        </div>
        <div class="file-item">
            <strong>backtest_report.json</strong><br>
            <small>30天模擬回測結果和性能分析</small>
        </div>
        <div class="file-item">
            <strong>index.html</strong><br>
            <small>本頁面，提供快速訪問鏈接</small>
        </div>
    </div>
    
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center;">
        <p>© 2025 AI選股分析系統 | 版本: 2.0 (修正路徑)</p>
        <p><small>⚠️ 免責聲明: 此分析僅供參考，不構成投資建議</small></p>
    </div>
</body>
</html>
HTML_EOF

echo "✅ 更新完成！"
echo ""
echo "📁 文件位置: $WEB_DIR"
echo "📋 文件列表:"
ls -lh "$WEB_DIR"
echo ""
echo "🌐 訪問方式:"
echo "1. file:///storage/emulated/0/bursasearch/myx_shop/web/ai_analysis_preview.html"
echo "2. 或直接打開: file:///storage/emulated/0/bursasearch/myx_shop/web/"
echo ""
echo "📅 完成時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================="
