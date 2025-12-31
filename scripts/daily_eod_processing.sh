#!/bin/bash
# 每日EOD处理 - 最终版

cd /storage/emulated/0/bursasearch/myx_shop/scripts

echo "📅 日期: $(date '+%Y-%m-%d %A')"

# 使用修复版脚本
python3 generate_json_from_eod_fixed_v2.py "/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"

# 处理生成的文件
DATA_DATE="20251230"
mkdir -p history ../web/history

if [ -f "picks_latest.json" ]; then
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    cp picks_latest.json latest_price.json data.json ../web/
    cp "history/picks_${DATA_DATE}.json" ../web/history/
    
    echo ""
    echo "✅ 处理完成！"
    echo "📅 数据日期: $DATA_DATE"
fi
