#!/bin/bash
echo "========================================"
echo "   🤖 AI選股完整工作流程"
echo "========================================"
echo "開始時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 設置路徑
BASE_DIR="/storage/shared/bursasearch"
SCRIPTS_DIR="$BASE_DIR/myx_shop/scripts"
DATA_SOURCE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
WEB_DIR="$BASE_DIR/myxshop"

# 步驟1: 檢查數據文件
echo "🔍 步驟1: 檢查數據源..."
LATEST_CSV=$(ls -t "$DATA_SOURCE"/*.csv 2>/dev/null | head -1)

if [ -z "$LATEST_CSV" ]; then
    echo "❌ 錯誤: 找不到CSV數據文件"
    echo "請檢查目錄: $DATA_SOURCE"
    exit 1
fi

echo "✅ 找到最新數據: $(basename "$LATEST_CSV")"
echo "📅 文件日期: $(stat -c %y "$LATEST_CSV" 2>/dev/null | cut -d' ' -f1)"

# 步驟2: 運行AI分析
echo ""
echo "🚀 步驟2: 運行AI選股分析..."
cd "$SCRIPTS_DIR"

if [ ! -f "ai_stock_picker.py" ]; then
    echo "❌ 錯誤: 找不到 ai_stock_picker.py"
    exit 1
fi

echo "正在分析數據，請稍候..."
python3 ai_stock_picker.py "$LATEST_CSV"

if [ $? -eq 0 ]; then
    echo "✅ AI分析完成"
else
    echo "❌ AI分析失敗"
    exit 1
fi

# 步驟3: 檢查生成的文件
echo ""
echo "📋 步驟3: 檢查生成結果..."
DATA_DIR="$SCRIPTS_DIR/data"

if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 錯誤: 數據目錄未創建"
    exit 1
fi

echo "📁 數據目錄內容:"
ls -la "$DATA_DIR/"

# 步驟4: 更新網站
echo ""
echo "🌐 步驟4: 更新網站數據..."
mkdir -p "$WEB_DIR"

# 複製所有JSON和HTML文件
echo "正在複製文件..."
for file in "$DATA_DIR"/*.json "$DATA_DIR"/*.html; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$WEB_DIR/$filename"
        echo "✅ 已複製: $filename"
    fi
done

# 創建更新標記
UPDATE_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "$UPDATE_TIME" > "$WEB_DIR/last_updated.txt"

# 創建簡單狀態頁面
cat > "$WEB_DIR/status.html" << STATUS_EOF
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>系統狀態</title></head>
<body style="font-family: Arial;">
    <h1>✅ AI選股系統正常運行</h1>
    <p>最後更新: $UPDATE_TIME</p>
    <p><a href="ai_analysis_preview.html">查看完整報告</a></p>
</body>
</html>
STATUS_EOF

echo "✅ 網站更新完成"

# 步驟5: 顯示總結
echo ""
echo "========================================"
echo "🎉 工作流程完成!"
echo "========================================"
echo "📊 數據源: $(basename "$LATEST_CSV")"
echo "📁 結果位置: $WEB_DIR"
echo ""
echo "可用文件:"
for file in "$WEB_DIR"/*; do
    if [ -f "$file" ]; then
        size=$(stat -c %s "$file" 2>/dev/null || echo "N/A")
        echo "  $(basename "$file") ($((size/1024)) KB)"
    fi
done
echo ""
echo "🌐 快速訪問:"
echo "1. 完整報告: file://$WEB_DIR/ai_analysis_preview.html"
echo "2. JSON數據: file://$WEB_DIR/picks.json"
echo "3. 系統狀態: file://$WEB_DIR/status.html"
echo ""
echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
