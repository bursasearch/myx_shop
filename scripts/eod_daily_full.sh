#!/data/data/com.termux/files/usr/bin/bash
# eod_daily_full.sh - 明日EOD下载完整流程
# 包含：数据下载 + 格式检查 + 自动修复 + 推送更新

cd /storage/emulated/0/bursasearch/myx_shop

echo "🚀 BursaSearch 明日EOD完整流程"
echo "================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "重要提醒：您收了客户RM5，必须确保服务质量！"
echo ""

# 第1部分：下载EOD数据
echo "📥 第1步：下载EOD数据..."
echo "--------------------------"
# 这里放入你原本的EOD下载命令
# 例如：
# python3 scripts/download_eod_data.py
# 或
# bash scripts/eod_download.sh

echo "正在运行你的EOD下载脚本..."
# 如果不知道脚本名，可以列出查看
echo "可用的脚本："
ls scripts/*.py scripts/*.sh 2>/dev/null | grep -i "eod\|download" || echo "请手动运行你的EOD脚本"

read -p "按Enter继续（假设EOD下载已完成）..."

# 第2部分：检查数据格式
echo -e "\n🔍 第2步：检查数据格式..."
echo "--------------------------"
bash daily_health_check.sh

# 第3部分：自动修复格式问题
echo -e "\n🔧 第3步：自动修复格式问题..."
echo "--------------------------"
# 检查是否有需要修复的问题
if grep -r '="[0-9]' web/ data/json/ 2>/dev/null | head -1; then
    echo "发现格式问题，正在修复..."
    bash fix_all_json.sh
else
    echo "✅ 未发现格式问题，跳过修复"
fi

# 第4部分：验证修复结果
echo -e "\n✅ 第4步：验证修复结果..."
echo "--------------------------"
echo "检查关键文件："
for file in web/picks_latest.json web/*.json 2>/dev/null; do
    if [ -f "$file" ]; then
        if grep -q '="[0-9]' "$file" 2>/dev/null; then
            echo "  ❌ $(basename $file): 仍有问题"
        else
            echo "  ✅ $(basename $file): 正常"
        fi
    fi
done

# 第5部分：提交到GitHub
echo -e "\n🚀 第5步：提交更新到GitHub..."
echo "--------------------------"
echo "更改的文件："
git status --short web/*.json data/json/*.json 2>/dev/null || echo "无JSON文件更改"

read -p "是否提交并推送？(y/n): " confirm
if [ "$confirm" = "y" ]; then
    git add web/*.json data/json/*.json
    git commit -m "每日EOD更新: $(date '+%Y-%m-%d %H:%M:%S')
- 更新股票数据
- 检查并修复数据格式
- 确保RM5服务质量"
    
    echo "正在推送到GitHub..."
    git push
    echo "✅ 推送完成！"
else
    echo "❌ 跳过推送，请手动推送"
fi

# 第6部分：提醒手动测试
echo -e "\n📱 第6步：手动测试（必须做！）"
echo "--------------------------"
echo "重要：收钱要负责！必须手动测试！"
echo ""
echo "请立即在手机浏览器访问："
echo "🌐 https://bursasearch.github.io/myx_shop/"
echo ""
echo "测试项目："
echo "1. 页面能否正常打开"
echo "2. 6742是否显示正常（不是='6742'）"
echo "3. 投资计算器功能是否正常"
echo "4. 支付信息是否正确"
echo ""
echo "⏰ GitHub Pages更新需要1-2分钟"
echo "   如果显示旧版本，请等待后刷新"

echo -e "\n🎉 明日EOD流程完成！"
echo "========================"
echo "完成时间: $(date '+%H:%M:%S')"
echo "下次运行: 明天同一时间"
echo ""
echo "💡 记住："
echo "   收了RM5，就要提供可靠服务！"
echo "   每天手动测试是责任！"
