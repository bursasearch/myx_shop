#!/bin/bash
# 快速检查脚本 - 只检查不推送

cd /storage/emulated/0/bursasearch/myx_shop

echo "🔍 快速数据检查"
echo "时间: $(date '+%H:%M:%S')"
echo ""

# 检查数据格式
echo "1. 检查数据格式问题："
grep -r '="[0-9]' web/ data/json/ 2>/dev/null | head -5 || echo "✅ 未发现格式问题"

# 检查文件修改时间
echo -e "\n2. 文件更新状态："
for file in web/picks_latest.json web/latest_price.json; do
    if [ -f "$file" ]; then
        echo "  $(basename $file): 修改于 $(date -r "$file" '+%m-%d %H:%M')"
    fi
done

# 检查Git状态
echo -e "\n3. Git状态："
git status --short 2>/dev/null | head -5 || echo "  无更改"

echo -e "\n💡 如需修复运行: bash fix_all_json.sh"
echo "💡 如需推送运行: bash eod_daily_full.sh"
