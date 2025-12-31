#!/bin/bash

echo "🚀 处理EOD数据 - 修复版 v2"
echo "=========================="

# 源CSV文件
SOURCE_CSV="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"

# 改进的日期提取函数
extract_date_from_filename() {
    local filename="$1"
    filename=$(basename "$filename" .csv)
    
    echo "调试: 原始文件名 = $filename" >&2
    
    # 特殊处理: 25251230 -> 20251230
    if [[ "$filename" == "25251230" ]]; then
        echo "20251230"
        return 0
    fi
    
    # 其他模式...
    date '+%Y%m%d'
}

FILE_NAME=$(basename "$SOURCE_CSV")
echo "📁 源文件: $SOURCE_CSV"
echo "📄 文件名: $FILE_NAME"

# 手动设置正确的日期（因为文件名是25251230）
if [[ "$FILE_NAME" == "25251230.csv" ]]; then
    DATA_DATE="20251230"
    echo "📅 手动设置日期: $DATA_DATE (从 25251230 转为 20251230)"
else
    # 尝试自动提取
    DATA_DATE=$(extract_date_from_filename "$FILE_NAME")
    echo "📅 提取日期: $DATA_DATE"
fi

# 检查文件是否存在
if [ ! -f "$SOURCE_CSV" ]; then
    echo "❌ 找不到源文件: $SOURCE_CSV"
    exit 1
fi

echo "📊 文件大小: $(wc -c < "$SOURCE_CSV") bytes"

# 复制到当前目录
echo ""
echo "📋 复制文件到当前目录..."
cp "$SOURCE_CSV" .
WORKING_CSV=$(basename "$SOURCE_CSV")

# 运行Python脚本
echo ""
echo "▶️  运行Python脚本..."
python3 generate_json_from_eod.py "$WORKING_CSV"

if [ $? -ne 0 ]; then
    echo "❌ Python脚本执行失败"
    exit 1
fi

# 处理生成的文件
echo ""
echo "📁 处理生成的文件..."

if [ -f "picks_latest.json" ]; then
    echo "✅ 已生成 picks_latest.json"
    
    # 创建历史文件（使用正确的日期）
    mkdir -p history
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    echo "✅ 创建历史文件: picks_${DATA_DATE}.json"
    
    # 复制到web目录
    mkdir -p ../web/history
    cp picks_latest.json ../web/ 2>/dev/null && echo "✅ 复制到 ../web/"
    cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null && echo "✅ 复制到 ../web/history/"
    
    # 显示信息
    echo ""
    echo "📋 处理完成:"
    echo "  源文件: $FILE_NAME"
    echo "  数据日期: $DATA_DATE"
    echo "  历史文件: picks_${DATA_DATE}.json"
    
else
    echo "⚠️  未生成 picks_latest.json"
fi

echo ""
echo "========================================"
echo "🎉 处理完成！"
echo "📅 数据日期: $DATA_DATE"
echo "⏰ 完成时间: $(date '+%H:%M:%S')"
