#!/data/data/com.termux/files/usr/bin/bash
# tomorrow_complete.sh - 生成正确文件的明日脚本

cd /storage/emulated/0/bursasearch/myx_shop

echo "🚀 BursaSearch 明日完整流程"
echo "=============================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目标文件:"
echo "  1. web/history/picks_$(date +%Y%m%d).json"
echo "  2. web/latest_price.json"
echo "  3. web/picks_latest.json"
echo ""

# 获取明天的日期（马来西亚时间）
TOMORROW_DATE=$(date -d '+1 day' '+%Y-%m-%d')
TOMORROW_FILENAME=$(date -d '+1 day' '+%Y%m%d')
echo "明日日期: $TOMORROW_DATE"
echo "明日文件名: picks_${TOMORROW_FILENAME}.json"
echo ""

# 第1步：运行EOD处理器
echo "📥 第1步：运行EOD处理器..."
echo "--------------------------"
cd scripts

if [ -f "eod_processor.py" ]; then
    echo "运行 eod_processor.py..."
    python3 eod_processor.py
else
    echo "❌ eod_processor.py 不存在"
fi

echo ""

# 第2步：生成JSON文件
echo "📊 第2步：生成JSON文件..."
echo "--------------------------"
if [ -f "generate_json_from_eod.py" ]; then
    echo "运行 generate_json_from_eod.py..."
    python3 generate_json_from_eod.py
else
    echo "❌ generate_json_from_eod.py 不存在"
fi

echo ""

# 第3步：检查生成的文件
echo "🔍 第3步：检查生成的文件..."
echo "--------------------------"
cd /storage/emulated/0/bursasearch/myx_shop

echo "1. 检查web目录："
ls -la web/*.json web/history/*.json 2>/dev/null | tail -10

echo -e "\n2. 检查是否缺少必要文件："
MISSING_FILES=0

# 检查 picks_latest.json
if [ ! -f "web/picks_latest.json" ]; then
    echo "  ❌ 缺少: web/picks_latest.json"
    MISSING_FILES=$((MISSING_FILES + 1))
else
    echo "  ✅ 存在: web/picks_latest.json"
fi

# 检查 latest_price.json
if [ ! -f "web/latest_price.json" ]; then
    echo "  ❌ 缺少: web/latest_price.json"
    MISSING_FILES=$((MISSING_FILES + 1))
else
    echo "  ✅ 存在: web/latest_price.json"
fi

# 检查今天的history文件
TODAY_FILE="web/history/picks_$(date +%Y%m%d).json"
if [ ! -f "$TODAY_FILE" ]; then
    echo "  ❌ 缺少: $TODAY_FILE"
    MISSING_FILES=$((MISSING_FILES + 1))
    
    # 尝试从picks_latest.json创建
    if [ -f "web/picks_latest.json" ]; then
        echo "  尝试从picks_latest.json创建..."
        cp "web/picks_latest.json" "$TODAY_FILE"
        echo "  ✅ 已创建: $TODAY_FILE"
        MISSING_FILES=$((MISSING_FILES - 1))
    fi
else
    echo "  ✅ 存在: $TODAY_FILE"
fi

# 第4步：修复数据格式
echo -e "\n🔧 第4步：修复数据格式..."
echo "--------------------------"
echo "检查并修复 '=\"数字' 格式问题..."

FIX_COUNT=0
for dir in web web/history scripts; do
    if [ -d "$dir" ]; then
        for json_file in "$dir"/*.json 2>/dev/null; do
            if [ -f "$json_file" ] && grep -q '="[0-9]' "$json_file" 2>/dev/null; then
                echo "  修复: $json_file"
                sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$json_file"
                sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$json_file"
                FIX_COUNT=$((FIX_COUNT + 1))
            fi
        done
    fi
done

if [ $FIX_COUNT -gt 0 ]; then
    echo "✅ 修复了 $FIX_COUNT 个文件"
else
    echo "✅ 未发现格式问题"
fi

# 第5步：验证6742显示
echo -e "\n✅ 第5步：验证6742显示..."
echo "--------------------------"
echo "检查关键文件中的6742："

for file in web/picks_latest.json web/latest_price.json "$TODAY_FILE" 2>/dev/null; do
    if [ -f "$file" ]; then
        echo -n "  $(basename $file): "
        if grep -q '="6742"' "$file" 2>/dev/null; then
            echo "❌ 有问题（='6742'）"
        elif grep -q '"6742"' "$file" 2>/dev/null; then
            echo "✅ 正常（6742）"
        else
            echo "ℹ️  未包含6742"
        fi
    fi
done

# 第6步：推送到GitHub
echo -e "\n🚀 第6步：推送到GitHub..."
echo "--------------------------"
echo "Git状态："
git status --short web/*.json web/history/*.json 2>/dev/null | head -10

read -p "是否提交并推送？(y/n): " confirm
if [ "$confirm" = "y" ]; then
    git add web/*.json web/history/*.json
    git commit -m "明日EOD更新 $(date '+%Y-%m-%d %H:%M')
- 生成 picks_$(date +%Y%m%d).json
- 更新 latest_price.json
- 确保6742显示正常
- 满足retail-inv.html需求"
    
    echo "正在推送到GitHub..."
    git push
    echo "✅ 推送完成！"
else
    echo "❌ 跳过推送"
fi

# 第7步：最终提醒
echo -e "\n📱 第7步：手动测试（必须做！）"
echo "--------------------------"
echo "重要：确保retail-inv.html有正确数据！"
echo ""
echo "测试网站："
echo "🌐 https://bursasearch.github.io/myx_shop/retail-inv.html"
echo ""
echo "检查项目："
echo "1. 页面能否正常打开"
echo "2. 是否加载了 picks_$(date +%Y%m%d).json"
echo "3. 6742是否显示正常"
echo "4. 最新价格是否更新"
echo ""
echo "💡 提示：按F12打开开发者工具，查看网络请求"

echo -e "\n🎉 流程完成！"
echo "生成的文件："
ls -lh web/picks_latest.json web/latest_price.json "$TODAY_FILE" 2>/dev/null
