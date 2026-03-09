#!/data/data/com.termux/files/usr/bin/bash
# push_eod_update.sh - 完整 EOD 自動化腳本（修正版）
# 包含：處理 Bursa & SGX 數據、同步文件、推送到 GitHub

echo "==================================="
echo "🚀 完整 EOD 自動化流程 - $(date)"
echo "==================================="

# 設定變數
BASE_DIR="/storage/emulated/0/bursasearch/myx_shop"
DEEPSEEK_DIR="/storage/emulated/0/deepseek/bursa"
BURSA_EOD_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
SGX_EOD_DIR="/storage/emulated/0/eskay9761/stock_data/SGX_Data/EOD"
LOG_FILE="$BASE_DIR/logs/eod_$(date +%Y%m%d).log"

# 創建日誌目錄
mkdir -p "$BASE_DIR/logs"

{
    echo "📊 開始 EOD 處理..."
    echo "📅 日期: $(date +%Y%m%d)"

    ## ==================== 步驟1：進入工作目錄 ====================
    cd "$BASE_DIR" || exit 1
    echo "✅ 進入目錄: $(pwd)"

    ## ==================== 步驟2：處理 Bursa 數據 ====================
    echo "📥 處理 Bursa EOD CSV..."
    BURSA_FILE="$BURSA_EOD_DIR/$(date +%Y%m%d).csv"
    
    if [ -f "$BURSA_FILE" ]; then
        echo "✅ 找到 Bursa CSV: $BURSA_FILE"
        
        # 複製到 deepseek 目錄並處理
        cp "$BURSA_FILE" "$DEEPSEEK_DIR/"
        cd "$DEEPSEEK_DIR"
        python3 eod_processor.py "$BURSA_FILE"
        
        # 複製生成的 JSON 到正確位置
        if [ -f "picks_latest.json" ]; then
            cp picks_latest.json "$BASE_DIR/web/"
            cp picks_latest.json "$BASE_DIR/docs/web/"
            echo "✅ Bursa 數據已更新"
        fi
        
        cd "$BASE_DIR"
    else
        echo "⚠️ 找不到 Bursa CSV 文件: $BURSA_FILE"
    fi

    ## ==================== 步驟3：處理 SGX 數據 ====================
echo "📥 處理 SGX EOD DAT..."
SGX_FILE="$SGX_EOD_DIR/$(date +%Y%m%d).dat"
SGX_PROCESSOR_DIR="/storage/emulated/0/deepseek/sgx"  # ✅ 修正這裡！

if [ -f "$SGX_FILE" ]; then
    echo "✅ 找到 SGX DAT: $SGX_FILE"
    
    # 進入正確的 SGX 處理器目錄
    cd "$SGX_PROCESSOR_DIR"  # ✅ 使用修正後的路徑
    python3 sgx_eod_processor.py "$SGX_FILE"
    
    # 複製生成的 JSON 到正確位置
    if [ -f "sgx_picks_latest.json" ]; then
        cp sgx_picks_latest.json "$BASE_DIR/web/"
        cp sgx_picks_latest.json "$BASE_DIR/docs/web/"
        echo "✅ SGX 數據已更新"
    fi
    
    cd "$BASE_DIR"
else
    echo "⚠️ 找不到 SGX DAT 文件: $SGX_FILE"
fi

    ## ==================== 步驟4：同步所有文件到 docs/ ====================
    echo "📋 同步文件到 docs/ 目錄..."

    # 創建必要的目錄
    mkdir -p docs/web/history
    mkdir -p docs/history

    # 複製 HTML 文件
    cp -f web/*.html docs/web/ 2>/dev/null && echo "✅ 複製 HTML 到 docs/web/"
    cp -f *.html docs/ 2>/dev/null && echo "✅ 複製 HTML 到 docs/"

    # 複製 Bursa JSON 文件
    cp -f web/picks_latest.json docs/web/ 2>/dev/null && echo "✅ 複製 picks_latest.json"
    cp -f web/date_config.js docs/ 2>/dev/null && echo "✅ 複製 date_config.js"
    cp -rf web/history/picks_*.json docs/web/history/ 2>/dev/null && echo "✅ 複製 Bursa 歷史數據"

    # 複製 SGX JSON 文件
    cp -f web/sgx_picks_latest.json docs/web/ 2>/dev/null && echo "✅ 複製 sgx_picks_latest.json"
    cp -f web/sgx_date_config.js docs/ 2>/dev/null && echo "✅ 複製 sgx_date_config.js"
    cp -rf web/history/sgx_picks_*.json docs/history/ 2>/dev/null && echo "✅ 複製 SGX 歷史數據"

    # 複製其他必要文件
    cp -f web/*.js docs/web/ 2>/dev/null && echo "✅ 複製 JS 文件"
    mkdir -p docs/images
    cp -f images/* docs/images/ 2>/dev/null && echo "✅ 複製圖片"

    ## ==================== 步驟5：Git 操作 ====================
    echo "📦 Git 操作..."

    # 加入所有變更
    git add docs/ web/ *.html *.py *.sh

    # 檢查是否有變更
    if git diff --staged --quiet; then
        echo "ℹ️ 沒有新的變更"
    else
        # 提交變更
        git commit -m "每日EOD更新 - $(date +%Y%m%d)

- 更新 Bursa 數據（15支股票）
- 更新 SGX 數據（10支股票）
- 同步所有文件到 docs/ 目錄
- 更新時間: $(date '+%Y-%m-%d %H:%M:%S')"

        # 推送到 GitHub
        git push origin master
        echo "✅ 推送完成"
    fi

    ## ==================== 步驟6：清理暫存文件 ====================
    echo "🧹 清理暫存文件..."
    rm -f "$DEEPSEEK_DIR"/*.csv "$DEEPSEEK_DIR"/*.dat 2>/dev/null

    ## ==================== 步驟7：生成報告 ====================
    echo "📊 生成報告..."

    # 統計文件數量
    BURSA_COUNT=$(ls -1 docs/web/history/picks_*.json 2>/dev/null | wc -l)
    SGX_COUNT=$(ls -1 docs/history/sgx_picks_*.json 2>/dev/null | wc -l)

    cat > "$BASE_DIR/last_eod_report.txt" << EOF
===========================
📊 EOD 更新報告 - $(date +%Y-%m-%d)
===========================

✅ Bursa 歷史文件: $BURSA_COUNT 天
✅ SGX 歷史文件: $SGX_COUNT 天
✅ 最後更新: $(date '+%Y-%m-%d %H:%M:%S')

📁 文件位置:
   - Bursa: docs/web/bursa.html
   - SGX: docs/web/sgx.html
   - AI監控: docs/web/ai-monitor.html

🌐 GitHub Pages:
   https://bursasearch.github.io/myx_shop/
===========================
EOF

    echo "✅ 報告已生成"

} >> "$LOG_FILE" 2>&1

echo ""
echo "==================================="
echo "✅ EOD 自動化流程完成！"
echo "==================================="
echo "📋 查看日誌: tail -f $LOG_FILE"
echo "📊 查看報告: cat $BASE_DIR/last_eod_report.txt"