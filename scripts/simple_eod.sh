#!/bin/bash
# 最简单正确的EOD处理器

echo "📅 今天: $(date '+%Y-%m-%d')"

# 固定路径
SOURCE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"
WORKDIR="/storage/emulated/0/bursasearch/myx_shop/scripts"

if [ ! -f "$SOURCE" ]; then
    echo "❌ 找不到文件: $SOURCE"
    exit 1
fi

cd "$WORKDIR" || exit 1

echo "📁 处理: $(basename "$SOURCE")"
cp "$SOURCE" .

# 运行Python
python3 generate_json_from_eod.py "25251230.csv"

if [ $? -ne 0 ]; then
    echo "❌ 处理失败"
    exit 1
fi

# 使用正确的日期
DATA_DATE="20251230"

# 确保目录存在
mkdir -p history ../web/history

# 处理文件
if [ -f "picks_latest.json" ]; then
    # 历史文件
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    echo "✅ 历史: picks_${DATA_DATE}.json"
    
    # 复制到web
    cp picks_latest.json latest_price.json data.json ../web/ 2>/dev/null
    cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null
    
    echo "✅ 复制到web目录"
    
    echo ""
    echo "🎉 完成！"
    echo "📅 日期: $DATA_DATE"
    echo "⏰ 时间: $(date '+%H:%M:%S')"
else
    echo "⚠️  未生成 picks_latest.json"
fi
