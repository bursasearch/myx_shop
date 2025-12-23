#!/bin/bash
cd /storage/emulated/0/bursasearch/myx_shop

echo "🔍 检查retail-inv.html需求"
echo "============================="

echo "1. 查找所有JSON引用："
grep -o '"[^"]*\.json"' web/retail-inv.html | sort -u

echo -e "\n2. 查找JavaScript中的动态加载："
grep -n "fetch\|\.json\|ajax\|loadJSON\|getJSON" web/retail-inv.html | head -10

echo -e "\n3. 检查实际需要的文件："
echo "   web/目录现有文件："
ls web/*.json web/history/*.json 2>/dev/null

echo -e "\n4. 检查今天的文件："
TODAY=$(date '+%Y%m%d')
echo "   今天日期: $TODAY"
echo "   需要文件: web/history/picks_${TODAY}.json"
ls web/history/picks_${TODAY}.json 2>/dev/null || echo "   ❌ 不存在"

echo -e "\n💡 建议：运行 fix_missing_files.sh 修复"
