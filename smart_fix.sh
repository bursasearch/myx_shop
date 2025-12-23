#!/data/data/com.termux/files/usr/bin/bash
# 智能修復工具 - 處理各種 ="6742" 情況

cd /storage/emulated/0/bursasearch/myx_shop

echo "🤖 智能修復工具啟動"
echo "處理 ="6742" 問題的所有可能情況"
echo ""

# 備份
BACKUP="web/retail-inv_$(date +%Y%m%d_%H%M%S).html"
cp web/retail-inv.html "$BACKUP"
echo "📦 創建備份: $BACKUP"

# 情況1: 直接修復 ="6742"
echo "🔧 情況1: 修復單純的 =\"6742\""
sed -i 's/="6742"/6742/g' web/retail-inv.html

# 情況2: 修復標籤內的 ="6742"
echo "🔧 情況2: 修復標籤內的錯誤"
sed -i 's/<\([a-zA-Z][a-zA-Z0-9]*\) =\"6742\"/<\1 data-code=\"6742\"/g' web/retail-inv.html

# 情況3: 修復帶有額外屬性的 ="6742"
echo "🔧 情況3: 修復複雜情況"
sed -i 's/=\"6742\"\([^>]*\)>/data-code=\"6742\"\1>/g' web/retail-inv.html

# 情況4: 確保YTLPOWR正確顯示
echo "🔧 情況4: 優化顯示"
# 如果6742單獨出現，後面添加YTLPOWR
sed -i 's/\([^>]\)6742\([^<Y]\)/\16742 - YTLPOWR\2/g' web/retail-inv.html

echo ""
echo "✅ 智能修復完成"

echo ""
echo "📊 修復報告:"
echo "   備份文件: $BACKUP"
echo "   修復時間: $(date '+%H:%M:%S')"
echo "   修復策略: 4種情況處理"

echo ""
echo "🔍 修復後檢查:"
echo "   6742出現次數: $(grep -c '6742' web/retail-inv.html)"
echo "   錯誤語法剩餘: $(grep -c '="6742"' web/retail-inv.html || echo '0')"
echo ""
echo "   顯示樣本:"
grep "6742" web/retail-inv.html | head -2

echo ""
echo "💡 如果問題還在，可能是動態生成的內容"
echo "   需要檢查JavaScript代碼"
