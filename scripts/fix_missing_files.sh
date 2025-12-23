#!/bin/bash
# fix_missing_files.sh - 修复retail-inv.html所需的缺失文件

cd /storage/emulated/0/bursasearch/myx_shop

echo "🔧 修复缺失文件"
echo "时间: $(date '+%H:%M:%S')"
echo ""

TODAY=$(date '+%Y%m%d')
TODAY_FILE="web/history/picks_${TODAY}.json"

echo "今日日期: $TODAY"
echo "需要文件: $TODAY_FILE"
echo ""

# 1. 检查并创建今天的history文件
echo "1. 检查历史文件："
if [ ! -f "$TODAY_FILE" ]; then
    echo "  ❌ 缺少: $TODAY_FILE"
    
    # 尝试从最新文件复制
    if [ -f "web/picks_latest.json" ]; then
        echo "  从 picks_latest.json 创建..."
        cp "web/picks_latest.json" "$TODAY_FILE"
        echo "  ✅ 已创建: $TODAY_FILE"
    elif [ -f "web/history/picks_20251221.json" ]; then
        echo "  从 picks_20251221.json 创建..."
        cp "web/history/picks_20251221.json" "$TODAY_FILE"
        echo "  ✅ 已创建: $TODAY_FILE"
    else
        echo "  ⚠️  无法创建，无源文件"
    fi
else
    echo "  ✅ 已存在: $TODAY_FILE"
fi

# 2. 检查latest_price.json
echo -e "\n2. 检查最新价格文件："
if [ ! -f "web/latest_price.json" ]; then
    echo "  ❌ 缺少: web/latest_price.json"
    
    # 尝试从scripts目录复制
    if [ -f "scripts/latest_price.json" ]; then
        echo "  从 scripts/latest_price.json 复制..."
        cp "scripts/latest_price.json" "web/latest_price.json"
        echo "  ✅ 已创建: web/latest_price.json"
    else
        echo "  ⚠️  无法创建，无源文件"
    fi
else
    echo "  ✅ 已存在: web/latest_price.json"
fi

# 3. 检查picks_latest.json
echo -e "\n3. 检查最新选股文件："
if [ ! -f "web/picks_latest.json" ]; then
    echo "  ❌ 缺少: web/picks_latest.json"
    
    # 尝试从scripts目录复制
    if [ -f "scripts/picks_latest.json" ]; then
        echo "  从 scripts/picks_latest.json 复制..."
        cp "scripts/picks_latest.json" "web/picks_latest.json"
        echo "  ✅ 已创建: web/picks_latest.json"
    else
        echo "  ⚠️  无法创建，无源文件"
    fi
else
    echo "  ✅ 已存在: web/picks_latest.json"
fi

# 4. 修复所有文件的格式
echo -e "\n4. 修复数据格式："
for file in web/picks_latest.json web/latest_price.json "$TODAY_FILE" 2>/dev/null; do
    if [ -f "$file" ]; then
        echo -n "  检查 $(basename $file): "
        if grep -q '="[0-9]' "$file" 2>/dev/null; then
            echo "❌ 有问题，修复中..."
            sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$file"
            sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$file"
            sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$file"
            sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$file"
            echo "    ✅ 已修复"
        else
            echo "✅ 正常"
        fi
    fi
done

echo -e "\n📊 修复完成！"
echo "现有文件："
ls -lh web/picks_latest.json web/latest_price.json "$TODAY_FILE" 2>/dev/null
