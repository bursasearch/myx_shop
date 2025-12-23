#!/data/data/com.termux/files/usr/bin/bash
# 安全修復腳本 - 已有備份，放心使用

echo "🛡️  安全修復模式啟動"
echo "已有備份: retail-inv_backup.html"
echo "開始時間: $(date '+%H:%M:%S')"
echo ""

cd /storage/emulated/0/bursasearch/myx_shop

# 再次確認備份存在
if [ ! -f "web/retail-inv_backup.html" ]; then
    echo "❌ 備份文件不存在！停止操作"
    exit 1
fi

echo "✅ 確認備份存在:"
ls -lh web/retail-inv_backup.html
echo ""

# 檢查問題
echo "🔍 檢查問題..."
PROBLEMS=$(grep -c '="6742"' web/retail-inv.html || echo "0")
OTHER_PROBLEMS=$(grep -c '="[0-9]\{4\}"' web/retail-inv.html || echo "0")

echo "發現問題:"
echo "  • '=\"6742\"': $PROBLEMS 處"
echo "  • 其他股票代碼: $OTHER_PROBLEMS 處"
echo ""

if [ "$PROBLEMS" -eq 0 ] && [ "$OTHER_PROBLEMS" -eq 0 ]; then
    echo "🎉 沒有發現需要修復的問題！"
    echo "💡 您的網站已經是完美的！"
    exit 0
fi

# 執行修復
echo "🔧 執行修復..."
echo "1. 修復 '=\"6742\"' → '6742'"
sed -i 's/="6742"/6742/g' web/retail-inv.html

echo "2. 修復其他股票代碼"
sed -i 's/="\([0-9]\{4\}\)"/\1/g' web/retail-inv.html

echo ""

# 驗證修復
echo "✅ 驗證修復結果..."
AFTER_PROBLEMS=$(grep -c '="6742"' web/retail-inv.html || echo "0")

if [ "$AFTER_PROBLEMS" -eq 0 ]; then
    echo "🎯 修復成功！"
    echo "   已清除 $PROBLEMS 處 '=\"6742\"' 問題"
    echo "   已清除 $OTHER_PROBLEMS 處其他問題"
else
    echo "⚠️  還有 $AFTER_PROBLEMS 處未修復"
fi

echo ""
echo "📊 修復摘要:"
echo "   修復前問題: $((PROBLEMS + OTHER_PROBLEMS)) 處"
echo "   修復後問題: $AFTER_PROBLEMS 處"
echo "   修復時間: $(date '+%H:%M:%S')"
echo ""
echo "💡 重要提醒:"
echo "   1. 備份文件: web/retail-inv_backup.html"
echo "   2. 如需還原: cp web/retail-inv_backup.html web/retail-inv.html"
echo "   3. 測試網站: https://bursasearch.github.io/myx_shop/"
