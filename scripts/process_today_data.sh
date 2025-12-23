#!/bin/bash
# process_today_data.sh - 处理今日数据完整流程

cd /storage/emulated/0/bursasearch/myx_shop

echo "🚀 今日数据处理完整流程"
echo "==========================="
echo "开始时间: $(date '+%H:%M:%S')"
echo "CSV文件: /storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/20251222.csv"
echo ""

# 第1步：运行eod_processor.py
echo "📥 第1步：处理EOD数据..."
echo "--------------------------"
cd scripts

CSV_FILE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/20251222.csv"

if [ -f "$CSV_FILE" ]; then
    echo "处理文件: $(basename "$CSV_FILE")"
    echo "文件大小: $(du -h "$CSV_FILE" | cut -f1)"
    echo ""
    
    # 尝试运行eod_processor.py
    echo "运行 eod_processor.py..."
    python3 eod_processor.py "$CSV_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ eod_processor.py 成功"
    else
        echo "⚠️  eod_processor.py 可能有问题，尝试其他方式..."
        echo "运行: python3 eod_processor.py \"$CSV_FILE\" -o \"../data/processed/processed.json\""
        mkdir -p ../data/processed 2>/dev/null
        python3 eod_processor.py "$CSV_FILE" -o "../data/processed/processed.json"
    fi
else
    echo "❌ CSV文件不存在: $CSV_FILE"
    echo "请检查文件路径"
    exit 1
fi

# 第2步：运行其他处理脚本
echo -e "\n📊 第2步：生成JSON文件..."
echo "--------------------------"

echo "运行 generate_json_from_eod.py..."
python3 generate_json_from_eod.py

echo -e "\n运行 normalize_eod.py..."
python3 normalize_eod.py

# 第3步：检查生成的文件
echo -e "\n🔍 第3步：检查生成的文件..."
echo "--------------------------"
cd /storage/emulated/0/bursasearch/myx_shop

echo "web/目录文件："
ls -la web/*.json 2>/dev/null

echo -e "\nscripts/目录文件："
ls -la scripts/*.json 2>/dev/null | head -10

# 第4步：确保有今天的文件
echo -e "\n📅 第4步：确保今天的文件..."
TODAY=$(date '+%Y%m%d')
TODAY_FILE="web/history/picks_${TODAY}.json"

if [ ! -f "$TODAY_FILE" ]; then
    echo "创建今天的文件: $TODAY_FILE"
    
    if [ -f "web/picks_latest.json" ]; then
        cp "web/picks_latest.json" "$TODAY_FILE"
        sed -i "s/\"date\": \".*\"/\"date\": \"$(date '+%Y-%m-%d')\"/g" "$TODAY_FILE"
        sed -i "s/\"last_updated\": \".*\"/\"last_updated\": \"$(date '+%Y-%m-%d %H:%M:%S')\"/g" "$TODAY_FILE"
        echo "✅ 已创建: $TODAY_FILE"
    elif [ -f "scripts/picks_latest.json" ]; then
        cp "scripts/picks_latest.json" "$TODAY_FILE"
        sed -i "s/\"date\": \".*\"/\"date\": \"$(date '+%Y-%m-%d')\"/g" "$TODAY_FILE"
        echo "✅ 已创建: $TODAY_FILE"
    else
        echo "❌ 无法创建，无源文件"
    fi
else
    echo "✅ 已存在: $TODAY_FILE"
fi

# 第5步：修复数据格式
echo -e "\n🔧 第5步：修复数据格式..."
echo "--------------------------"
echo "修复 '=\"数字' 格式问题..."

for dir in web scripts; do
    if [ -d "$dir" ]; then
        for json_file in "$dir"/*.json 2>/dev/null; do
            if [ -f "$json_file" ] && grep -q '="[0-9]' "$json_file" 2>/dev/null; then
                echo "  修复: $json_file"
                sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$json_file"
                sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$json_file"
            fi
        done
    fi
done

# 第6步：验证6742
echo -e "\n✅ 第6步：验证6742显示..."
echo "--------------------------"
echo "检查关键文件："

for file in web/picks_latest.json web/latest_price.json "$TODAY_FILE" 2>/dev/null; do
    if [ -f "$file" ]; then
        echo -n "  $(basename $file): "
        if grep -q '="6742"' "$file" 2>/dev/null; then
            echo "❌ 有问题（='6742'）"
        elif grep -q '"6742"' "$file" 2>/dev/null; then
            echo "✅ 正常（6742）"
        else
            # 显示文件中的股票代码示例
            echo -n "ℹ️  未包含6742，包含："
            grep -o '"code": "[^"]*"' "$file" 2>/dev/null | head -3 | tr '\n' ' '
            echo ""
        fi
    fi
done

echo -e "\n🎉 数据处理完成！"
echo "时间: $(date '+%H:%M:%S')"
echo "下一步："
echo "  1. 访问网页测试"
echo "  2. 推送到GitHub"
echo "  3. 确认6742显示正常"
