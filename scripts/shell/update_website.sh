#!/bin/bash
echo "========================================"
echo "   🚀 AI選股網站更新系統"
echo "========================================"
echo "$(date '+%Y-%m-%d %H:%M:%S') 開始更新..."

# 設置路徑
BASE_DIR="/storage/shared/bursasearch"
SCRIPTS_DIR="$BASE_DIR/myx_shop/scripts"
DATA_DIR="$SCRIPTS_DIR/data"
WEB_DIR="$BASE_DIR/myxshop"

echo "📁 腳本目錄: $SCRIPTS_DIR"
echo "📁 數據目錄: $DATA_DIR"
echo "📁 網站目錄: $WEB_DIR"

# 確保目錄存在
mkdir -p "$WEB_DIR"

# 步驟1: 檢查AI分析結果
echo "🔍 檢查AI分析結果..."
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 數據目錄不存在，請先運行AI分析"
    exit 1
fi

# 步驟2: 複製文件
echo "📋 複製文件到網站目錄..."

# 複製 picks.json
if [ -f "$DATA_DIR/picks.json" ]; then
    cp "$DATA_DIR/picks.json" "$WEB_DIR/picks.json"
    echo "✅ picks.json 已複製"
else
    echo "⚠️  找不到 picks.json"
fi

# 複製 backtest_report.json
if [ -f "$DATA_DIR/backtest_report.json" ]; then
    cp "$DATA_DIR/backtest_report.json" "$WEB_DIR/backtest_report.json"
    echo "✅ backtest_report.json 已複製"
else
    echo "⚠️  找不到 backtest_report.json"
fi

# 複製 HTML 報告
if [ -f "$DATA_DIR/ai_analysis_preview.html" ]; then
    cp "$DATA_DIR/ai_analysis_preview.html" "$WEB_DIR/ai_analysis_preview.html"
    echo "✅ HTML報告已複製"
else
    echo "⚠️  找不到 HTML報告"
fi

# 步驟3: 更新時間戳
echo "🕐 更新時間戳..."
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP" > "$WEB_DIR/last_update.txt"

# 步驟4: 創建簡單的index.html
echo "📄 創建首頁..."
cat > "$WEB_DIR/index.html" << HTML_EOF
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI選股分析結果</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #4a6fa5; color: white; padding: 20px; border-radius: 5px; }
        .file-list { margin: 20px 0; }
        .file-item { 
            background: #f8f9fa; 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
        }
        .btn {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI選股分析系統</h1>
        <p>最後更新: $TIMESTAMP</p>
    </div>
    
    <div class="file-list">
        <div class="file-item">
            <h3>🎯 股票推薦數據</h3>
            <p>包含所有推薦股票的詳細信息</p>
            <a href="picks.json" class="btn" target="_blank">查看JSON數據</a>
        </div>
        
        <div class="file-item">
            <h3>📈 回測分析報告</h3>
            <p>模擬回測結果和性能分析</p>
            <a href="backtest_report.json" class="btn" target="_blank">查看回測報告</a>
        </div>
        
        <div class="file-item">
            <h3>🌐 完整HTML報告</h3>
            <p>圖形化界面展示分析結果</p>
            <a href="ai_analysis_preview.html" class="btn" target="_blank">查看完整報告</a>
        </div>
    </div>
    
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>© 2025 AI選股分析系統 | 更新頻率: 每日</p>
        <p>免責聲明: 此分析僅供參考，不構成投資建議</p>
    </div>
</body>
</html>
HTML_EOF

echo "✅ 首頁已創建"

# 步驟5: 顯示結果
echo ""
echo "========================================"
echo "🎉 網站更新完成!"
echo "========================================"
echo "📁 文件位置: $WEB_DIR"
echo ""
echo "可用文件:"
ls -la "$WEB_DIR" | grep -v "^total"
echo ""
echo "💡 訪問方式:"
echo "1. 本地瀏覽器: file://$WEB_DIR/index.html"
echo "2. 或直接打開: file://$WEB_DIR/ai_analysis_preview.html"
echo "