#!/bin/bash
# 使用修复版的Python脚本处理EOD数据

echo "🚀 EOD数据处理 (修复股票代码版)"
echo "==============================="

cd /storage/emulated/0/bursasearch/myx_shop/scripts

# 查找最新的EOD文件
EOD_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
CSV_FILE=$(ls -t "$EOD_DIR"/*.csv 2>/dev/null | head -1)

if [ -z "$CSV_FILE" ] || [ ! -f "$CSV_FILE" ]; then
    echo "❌ 找不到EOD CSV文件"
    exit 1
fi

echo "📁 处理文件: $(basename "$CSV_FILE")"

# 复制到当前目录
cp "$CSV_FILE" .
WORKING_CSV=$(basename "$CSV_FILE")

# 从文件名提取日期（智能处理25251230 -> 20251230）
if [[ "$WORKING_CSV" == "25251230.csv" ]]; then
    DATA_DATE="20251230"
else
    # 尝试提取8位数字日期
    if [[ "$WORKING_CSV" =~ ([0-9]{8}) ]]; then
        DATE_NUM="${BASH_REMATCH[1]}"
        # 如果是25251230格式，转为20251230
        if [[ "$DATE_NUM" == "25251230" ]]; then
            DATA_DATE="20251230"
        else
            DATA_DATE="$DATE_NUM"
        fi
    else
        DATA_DATE=$(date '+%Y%m%d')
    fi
fi

echo "📅 数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"

# 备份原来的Python脚本
if [ -f "generate_json_from_eod.py" ]; then
    cp generate_json_from_eod.py generate_json_from_eod.py.backup
    echo "✅ 备份原脚本"
fi

# 使用修复版脚本
echo ""
echo "▶️  运行修复版Python脚本..."
cp generate_json_from_eod_fixed.py generate_json_from_eod.py
python3 generate_json_from_eod.py "$WORKING_CSV"

# 恢复原脚本（如果需要）
if [ -f "generate_json_from_eod.py.backup" ]; then
    mv generate_json_from_eod.py.backup generate_json_from_eod.py
fi

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
    
    # 检查是否有问题代码
    PROBLEM_CODES=$(grep -o '"code": *"[^"]*"' picks_latest.json | grep -E '"(=|MR|CW|CA|\\\\)' | head -5)
    
    if [ -n "$PROBLEM_CODES" ]; then
        echo "⚠️  发现可能的问题代码:"
        echo "$PROBLEM_CODES" | sed 's/^/  /g'
        echo ""
        echo "建议运行修复脚本: bash fix_stock_codes.sh"
    else
        echo "✅ 股票代码格式正常"
    fi
    
    echo ""
    echo "🎉 处理完成！"
    echo "📅 日期: $DATA_DATE"
    echo "⏰ 时间: $(date '+%H:%M:%S')"
else
    echo "⚠️  未生成 picks_latest.json"
fi
