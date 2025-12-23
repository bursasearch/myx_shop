#!/bin/bash
cd /storage/emulated/0/bursasearch/myx_shop

echo "🔧 修复页面日期显示（基于真实文件）"
echo "======================================"

# 获取真实存在的日期
echo "真实存在的日期文件："
REAL_DATES=()
for file in web/history/picks_*.json; do
    if [ -f "$file" ]; then
        DATE=$(basename "$file" | sed 's/picks_\(.*\)\.json/\1/')
        REAL_DATES+=("$DATE")
        echo "  ✅ $DATE"
    fi
done

echo -e "\n缺失的日期："
# 检查哪些日期应该存在但缺失
START_DATE="20251215"
END_DATE="20251222"

current=$START_DATE
while [[ $current -le $END_DATE ]]; do
    if [[ ! " ${REAL_DATES[@]} " =~ " ${current} " ]]; then
        echo "  ❌ $current (缺失)"
    fi
    current=$(date -d "$current +1 day" +%Y%m%d 2>/dev/null || break)
done

echo -e "\n📋 建议："
echo "1. 页面应该只显示这些真实日期：${REAL_DATES[*]}"
echo "2. 不要显示20251219（不存在）"
echo "3. 不要显示20251222（今天，未生成）"

# 检查页面是否有硬编码的20251219
echo -e "\n🔍 检查页面是否有20251219："
if grep -q "20251219\|2025-12-19" web/retail-inv.html; then
    echo "  ❌ 页面包含不存在的2025-12-19"
    echo "  需要修复页面代码"
else
    echo "  ✅ 页面没有硬编码2025-12-19"
fi
