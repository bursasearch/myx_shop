#!/bin/bash
# 修复历史文件日期

cd /storage/emulated/0/bursasearch/myx_shop/scripts

echo "🔧 修复历史文件日期"
echo "=================="

# 检查所有历史文件
echo "📁 当前历史文件:"
ls -la history/*.json 2>/dev/null

echo ""
echo "📁 Web历史文件:"
ls -la ../web/history/*.json 2>/dev/null 2>/dev/null

# 修复错误命名的文件
echo ""
echo "🔄 修复文件..."

# 如果有 20252512.json，修复为 20251230.json
if [ -f "history/picks_20252512.json" ]; then
    mv "history/picks_20252512.json" "history/picks_20251230.json"
    echo "✅ 修复: history/picks_20252512.json → history/picks_20251230.json"
fi

if [ -f "../web/history/picks_20252512.json" ]; then
    mv "../web/history/picks_20252512.json" "../web/history/picks_20251230.json"
    echo "✅ 修复: web/history/picks_20252512.json → web/history/picks_20251230.json"
fi

# 确保最新文件链接正确
if [ -f "picks_latest.json" ] && [ -f "history/picks_20251230.json" ]; then
    # 检查是否需要更新
    if [ "picks_latest.json" -nt "history/picks_20251230.json" ]; then
        cp picks_latest.json "history/picks_20251230.json"
        echo "✅ 更新历史文件为最新内容"
    fi
    
    # 确保web目录有最新文件
    cp picks_latest.json ../web/ 2>/dev/null
    cp "history/picks_20251230.json" ../web/history/ 2>/dev/null
fi

echo ""
echo "📋 最终状态:"
echo "1. 历史目录:"
ls -la history/picks_2025*.json 2>/dev/null

echo ""
echo "2. Web目录:"
ls -la ../web/history/picks_2025*.json 2>/dev/null 2>/dev/null

echo ""
echo "🎉 修复完成！"
