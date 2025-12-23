#!/bin/bash
echo "🧪 本地測試模式"
echo "測試修復後的HTML，不影響線上網站"
echo ""

cd /storage/emulated/0/bursasearch/myx_shop

echo "1. 語法檢查..."
# 檢查HTML基本語法
echo "   文件大小: $(wc -l < web/retail-inv.html) 行"
echo "   文件大小: $(du -h web/retail-inv.html | cut -f1)"

echo ""
echo "2. 股票代碼檢查..."
# 檢查所有股票代碼
echo "   6742 出現次數: $(grep -c '6742' web/retail-inv.html || echo "0")"
echo "   1066 出現次數: $(grep -c '1066' web/retail-inv.html || echo "0")"
echo "   1155 出現次數: $(grep -c '1155' web/retail-inv.html || echo "0")"

echo ""
echo "3. 錯誤語法檢查..."
ERRORS=$(grep -c '="[0-9]\{4\}"' web/retail-inv.html || echo "0")
if [ "$ERRORS" -eq 0 ]; then
    echo "   ✅ 無錯誤語法"
else
    echo "   ❌ 還有 $ERRORS 處錯誤"
fi

echo ""
echo "4. 快速內容預覽..."
echo "   ================================="
grep -B1 -A1 "6742" web/retail-inv.html | head -6
echo "   ================================="

echo ""
echo "📱 本地測試方法:"
echo "   1. 在手機文件管理器找到:"
echo "      /storage/emulated/0/bursasearch/myx_shop/web/retail-inv.html"
echo "   2. 用瀏覽器打開查看效果"
echo "   3. 確認6742顯示正常"
echo ""
echo "⚠️  重要：這是本地測試，不會影響線上網站！"
echo "   滿意後再推送到GitHub。"
