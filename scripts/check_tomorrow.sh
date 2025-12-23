#!/bin/bash
# check_tomorrow.sh - 明日快速检查脚本

cd /storage/emulated/0/bursasearch/myx_shop

echo "🔍 明日快速检查"
echo "时间: $(date '+%H:%M:%S')"
echo ""

# 1. 检查scripts目录
echo "1. 检查scripts目录："
cd scripts
echo "   JSON文件："
ls *.json 2>/dev/null | head -5

echo -e "\n   Python脚本："
ls *.py | grep -i "eod\|generate\|normalize" | head -5

# 2. 检查6742显示
echo -e "\n2. 检查6742显示："
cd /storage/emulated/0/bursasearch/myx_shop

for file in web/picks_latest.json scripts/picks_latest.json 2>/dev/null; do
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

# 3. 检查数据格式问题
echo -e "\n3. 检查数据格式："
ERRORS=$(grep -r '="[0-9]' scripts/ web/ data/json/ 2>/dev/null | wc -l)
if [ "$ERRORS" -gt 0 ]; then
    echo "  ❌ 发现 $ERRORS 处格式问题"
    grep -r '="[0-9]' scripts/ web/ data/json/ 2>/dev/null | head -3
else
    echo "  ✅ 未发现格式问题"
fi

# 4. 明日操作提醒
echo -e "\n📋 明日操作："
echo "  cd /storage/emulated/0/bursasearch/myx_shop/scripts"
echo "  bash tomorrow_eod.sh"
echo ""
echo "💡 记得：收钱要负责，手动测试网站！"
