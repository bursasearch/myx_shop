#!/bin/bash

echo "🚀 处理EOD数据 - 修复版"
echo "======================="

# 源CSV文件
SOURCE_CSV="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"

# 目标日期（从文件名提取）
# 注意：文件名是 25251230.csv，看起来像是 20251230
# 但前两位是25不是20，可能是格式问题
FILE_NAME=$(basename "$SOURCE_CSV" .csv)
echo "📁 源文件: $SOURCE_CSV"
echo "📄 文件名: $FILE_NAME"

# 从文件名提取日期（假设格式是 YYMMDD 或 MMDD）
if [[ "$FILE_NAME" =~ ([0-9]{2})([0-9]{2})([0-9]{2}) ]]; then
    # 假设是 YYMMDD 格式，转为 YYYYMMDD
    YEAR_PREFIX="20"  # 假设是20xx年
    YEAR="${YEAR_PREFIX}${BASH_REMATCH[1]}"
    MONTH="${BASH_REMATCH[2]}"
    DAY="${BASH_REMATCH[3]}"
    DATA_DATE="${YEAR}${MONTH}${DAY}"
    echo "📅 从文件名提取日期: $DATA_DATE"
else
    # 使用今天日期
    DATA_DATE=$(date '+%Y%m%d')
    echo "⚠️  无法从文件名提取日期，使用今天: $DATA_DATE"
fi

# 检查文件是否存在
if [ ! -f "$SOURCE_CSV" ]; then
    echo "❌ 找不到源文件: $SOURCE_CSV"
    exit 1
fi

echo "📊 文件大小: $(wc -c < "$SOURCE_CSV" 2>/dev/null || echo "未知") bytes"

# 复制到当前目录（可选）
echo ""
echo "📋 复制文件到当前目录..."
cp "$SOURCE_CSV" .
WORKING_CSV=$(basename "$SOURCE_CSV")

# 运行Python脚本
echo ""
echo "▶️  运行Python脚本..."
python3 generate_json_from_eod.py "$WORKING_CSV"

PYTHON_EXIT=$?
if [ $PYTHON_EXIT -ne 0 ]; then
    echo "❌ Python脚本执行失败 (退出码: $PYTHON_EXIT)"
    
    # 尝试其他可能的编码
    echo ""
    echo "🔄 尝试诊断问题..."
    
    # 查看CSV文件前几行
    echo "📄 CSV文件前5行:"
    head -5 "$WORKING_CSV" 2>/dev/null || echo "无法读取文件"
    
    # 查看文件编码
    echo ""
    echo "🔍 文件信息:"
    file -i "$WORKING_CSV" 2>/dev/null || echo "无法检测文件类型"
    
    exit 1
fi

# 处理生成的文件
echo ""
echo "📁 处理生成的文件..."

if [ -f "picks_latest.json" ]; then
    echo "✅ 已生成 picks_latest.json"
    
    # 检查文件是否为空
    FILE_SIZE=$(wc -c < "picks_latest.json")
    if [ "$FILE_SIZE" -lt 100 ]; then
        echo "⚠️  警告: picks_latest.json 可能为空 ($FILE_SIZE bytes)"
    else
        echo "📊 文件大小: $FILE_SIZE bytes"
    fi
    
    # 创建历史文件
    mkdir -p history
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    echo "✅ 创建历史文件: picks_${DATA_DATE}.json"
    
    # 复制到web目录
    mkdir -p ../web/history
    cp picks_latest.json ../web/ 2>/dev/null && echo "✅ 复制到 ../web/"
    cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null && echo "✅ 复制到 ../web/history/"
    
    # 显示JSON内容预览
    echo ""
    echo "📋 JSON预览:"
    head -5 "picks_latest.json" 2>/dev/null || echo "无法预览"
    
else
    echo "⚠️  未生成 picks_latest.json"
    
    # 检查生成了哪些文件
    echo "📂 当前目录JSON文件:"
    ls -la *.json 2>/dev/null || echo "没有JSON文件"
    
    # 检查Python脚本的输出
    echo ""
    echo "🔍 检查Python输出:"
    echo "可能的原因:"
    echo "1. CSV格式不正确"
    echo "2. 文件编码问题"
    echo "3. 数据列不匹配"
fi

echo ""
echo "========================================"
echo "🎉 处理完成！"
echo "📅 数据日期: $DATA_DATE"
echo "⏰ 完成时间: $(date '+%H:%M:%S')"
