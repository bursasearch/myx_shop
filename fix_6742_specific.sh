#!/data/data/com.termux/files/usr/bin/bash
# 專門修復圖片中的 ="6742" 問題

echo "🎯 專門修復 ="6742" 問題"
echo "針對圖片中的錯誤語法"
echo "時間: $(date '+%H:%M:%S')"
echo ""

cd /storage/emulated/0/bursasearch/myx_shop

# 再次確認備份
if [ -f "web/retail-inv_backup.html" ]; then
    echo "✅ 備份文件存在: retail-inv_backup.html"
    BACKUP_SIZE=$(du -h web/retail-inv_backup.html | cut -f1)
    echo "   備份大小: $BACKUP_SIZE"
else
    echo "⚠️  未找到備份文件，創建新備份..."
    cp web/retail-inv.html "web/retail-inv_backup_$(date +%Y%m%d_%H%M%S).html"
fi

echo ""
echo "🔍 詳細檢查問題..."

# 查找所有 ="6742" 出現的位置
echo "查找 '=\"6742\"' 出現位置:"
grep -n '="6742"' web/retail-inv.html | while read line; do
    LINE_NUM=$(echo "$line" | cut -d: -f1)
    CONTEXT=$(sed -n "${LINE_NUM}p" web/retail-inv.html)
    echo "   第 $LINE_NUM 行: $CONTEXT"
done

echo ""
echo "查找類似問題 (=\"數字\"):"
grep -n '="[0-9]\{4\}"' web/retail-inv.html | head -5

echo ""
echo "📊 問題統計:"
PROBLEM_6742=$(grep -c '="6742"' web/retail-inv.html || echo "0")
PROBLEM_OTHER=$(grep -c '="[0-9]\{4\}"' web/retail-inv.html || echo "0")
echo "   • '=\"6742\"': $PROBLEM_6742 處"
echo "   • 其他股票代碼: $((PROBLEM_OTHER - PROBLEM_6742)) 處"
echo "   • 總問題: $PROBLEM_OTHER 處"

if [ "$PROBLEM_6742" -eq 0 ]; then
    echo ""
    echo "🎉 沒有發現 '=\"6742\"' 問題！"
    echo "💡 可能問題在其他文件？"
    exit 0
fi

echo ""
echo "🔧 開始修復..."
echo "1. 修復 '=\"6742\"' → '6742'"
sed -i 's/="6742"/6742/g' web/retail-inv.html

echo "2. 修復其他 '=\"數字\"' → '數字'"
sed -i 's/="\([0-9]\{4\}\)"/\1/g' web/retail-inv.html

echo "3. 優化顯示：添加股票符號"
# 在6742後面添加YTLPOWR（如果還沒有的話）
sed -i 's/6742\([^>]*\)>\([^<]*\)<[^>]*>YTLPOWR/6742\1>\2 - YTLPOWR/g' web/retail-inv.html

echo ""
echo "✅ 修復完成！"

echo ""
echo "🧪 驗證修復結果..."
AFTER_6742=$(grep -c '="6742"' web/retail-inv.html || echo "0")
AFTER_OTHER=$(grep -c '="[0-9]\{4\}"' web/retail-inv.html || echo "0")

if [ "$AFTER_6742" -eq 0 ]; then
    echo "   ✅ '=\"6742\"' 問題已完全解決"
    echo "   修復了 $PROBLEM_6742 處問題"
else
    echo "   ⚠️  還有 $AFTER_6742 處未修復"
fi

echo ""
echo "📝 修復後樣本:"
grep -n "6742" web/retail-inv.html | head -3 | while read line; do
    echo "   $line"
done

echo ""
echo "🌐 測試建議:"
echo "   1. 本地測試: file:///storage/emulated/0/bursasearch/myx_shop/web/retail-inv.html"
echo "   2. 確認6742顯示為: 6742 或 6742 - YTLPOWR"
echo "   3. 確認沒有 '=\"' 前綴"
echo ""
echo "🛡️  安全提示:"
echo "   如需還原: cp web/retail-inv_backup.html web/retail-inv.html"
