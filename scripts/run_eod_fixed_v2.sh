#!/bin/bash
# 使用修复版v2处理EOD数据

echo "🚀 EOD数据处理 v2.0"
echo "=================="

cd /storage/emulated/0/bursasearch/myx_shop/scripts

# 查找CSV文件
CSV_FILE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 找不到文件: $CSV_FILE"
    exit 1
fi

echo "📁 处理文件: $(basename "$CSV_FILE")"
cp "$CSV_FILE" .

# 设置日期
DATA_DATE="20251230"
echo "📅 数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"

# 运行修复版v2
echo ""
echo "▶️  运行修复版Python脚本 v2..."
python3 generate_json_from_eod_fixed_v2.py "25251230.csv"

if [ $? -ne 0 ]; then
    echo "❌ Python脚本执行失败"
    exit 1
fi

# 处理生成的文件
echo ""
echo "📁 保存文件..."

mkdir -p history ../web/history

if [ -f "picks_latest.json" ]; then
    # 复制历史文件
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    echo "✅ 历史文件: picks_${DATA_DATE}.json"
    
    # 复制到web目录
    cp picks_latest.json latest_price.json data.json ../web/ 2>/dev/null
    cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null
    echo "✅ 复制到web目录"
    
    # 验证股票代码
    echo ""
    echo "🔍 验证股票代码格式..."
    
    # 检查示例
    echo "前5个股票代码:"
    grep -o '"code": *"[^"]*"' picks_latest.json | head -5 | sed 's/"code": "/  /g; s/"$//g'
    
    # 检查是否有问题代码
    PROBLEM_CODES=$(grep -o '"code": *"[^"]*"' picks_latest.json | grep -E '"(=|MR|CW|CA|\\\\)' | head -3)
    
    if [ -n "$PROBLEM_CODES" ]; then
        echo ""
        echo "⚠️  发现可能的问题代码，运行快速修复..."
        bash quick_fix_json.sh
    else
        echo "✅ 股票代码格式正常"
    fi
    
    echo ""
    echo "🎉 处理完成！"
    echo "📅 日期: $DATA_DATE"
    echo "⏰ 时间: $(date '+%H:%M:%S')"
else
    echo "⚠️  未生成 picks_latest.json"
    echo "检查错误信息..."
fi
