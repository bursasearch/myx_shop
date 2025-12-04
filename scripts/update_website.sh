#!/bin/bash

# update_website.sh - 自動更新網站AI選股數據

echo "========================================"
echo "   🌐 AI選股網站自動更新腳本             "
echo "========================================"

# 設定參數
AI_WORKFLOW_DIR="/data/data/com.termux/files/home"
WEBSITE_DIR="/data/data/com.termux/files/home/myx_shop"
LOG_FILE="$WEBSITE_DIR/logs/website_update_$(date +%Y%m%d).log"

# 建立日誌目錄
mkdir -p "$(dirname "$LOG_FILE")"

# 記錄開始時間
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始更新網站數據..." | tee -a "$LOG_FILE"

# 步驟1: 運行AI工作流（如果尚未運行）
echo "[$(date '+%H:%M:%S')] 步驟1: 檢查AI工作流..." | tee -a "$LOG_FILE"

if [ ! -f "$AI_WORKFLOW_DIR/ai_selected_stocks_$(date +%Y%m%d).txt" ]; then
    echo "  📥 AI工作流未運行，執行中..." | tee -a "$LOG_FILE"
    cd "$AI_WORKFLOW_DIR"
    ./daily_ai_workflow.sh >> "$LOG_FILE" 2>&1
else
    echo "  ✅ AI工作流已運行" | tee -a "$LOG_FILE"
fi

# 步驟2: 轉換數據格式
echo "[$(date '+%H:%M:%S')] 步驟2: 轉換數據格式..." | tee -a "$LOG_FILE"
cd "$WEBSITE_DIR"

if [ -f "js/update_ai_data.js" ]; then
    node js/update_ai_data.js >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✅ 數據轉換成功" | tee -a "$LOG_FILE"
    else
        echo "  ❌ 數據轉換失敗" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "  ❌ 找不到 update_ai_data.js" | tee -a "$LOG_FILE"
    exit 1
fi

# 步驟3: 檢查數據文件
echo "[$(date '+%H:%M:%S')] 步驟3: 檢查生成的文件..." | tee -a "$LOG_FILE"

if [ -f "website_data/ai_stocks_latest.json" ]; then
    STOCK_COUNT=$(grep -c '"code"' website_data/ai_stocks_latest.json)
    echo "  📊 生成 $STOCK_COUNT 支股票數據" | tee -a "$LOG_FILE"
else
    echo "  ❌ 未生成數據文件" | tee -a "$LOG_FILE"
    exit 1
fi

# 步驟4: 提交到GitHub
echo "[$(date '+%H:%M:%S')] 步驟4: 提交到GitHub..." | tee -a "$LOG_FILE"

cd "$WEBSITE_DIR"

# 檢查是否有變更
if git status --porcelain | grep -q "."; then
    echo "  📝 發現變更，提交中..." | tee -a "$LOG_FILE"
    
    git add website_data/ >> "$LOG_FILE" 2>&1
    git commit -m "更新AI選股數據 $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✅ GitHub提交成功" | tee -a "$LOG_FILE"
        
        # 顯示更新摘要
        echo "" | tee -a "$LOG_FILE"
        echo "📈 更新摘要:" | tee -a "$LOG_FILE"
        echo "  • 日期: $(date '+%Y-%m-%d')" | tee -a "$LOG_FILE"
        echo "  • 股票數量: $STOCK_COUNT" | tee -a "$LOG_FILE"
        echo "  • 網站: https://bursasearch.github.io/myx_shop/stocks.html" | tee -a "$LOG_FILE"
        echo "  • 數據文件: website_data/ai_stocks_latest.json" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        
    else
        echo "  ❌ GitHub提交失敗" | tee -a "$LOG_FILE"
    fi
else
    echo "  ⏭️  無變更，跳過提交" | tee -a "$LOG_FILE"
fi

# 步驟5: 清理舊日誌
echo "[$(date '+%H:%M:%S')] 步驟5: 清理舊日誌..." | tee -a "$LOG_FILE"
find "$WEBSITE_DIR/logs" -name "website_update_*.log" -mtime +7 -delete
echo "  ✅ 清理完成" | tee -a "$LOG_FILE"

# 完成
echo "[$(date '+%H:%M:%S')] 🎉 網站更新流程完成！" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
