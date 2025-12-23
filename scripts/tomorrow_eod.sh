#!/data/data/com.termux/files/usr/bin/bash
# tomorrow_eod.sh - 明日EOD完整流程（scripts目录版）

cd /storage/emulated/0/bursasearch/myx_shop/scripts

echo "🚀 BursaSearch 明日EOD流程 (scripts目录版)"
echo "=========================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目录: $(pwd)"
echo "重要提醒：您收了客户RM5，必须确保服务质量！"
echo ""

# 第1部分：EOD数据处理
echo "📊 第1步：处理EOD数据..."
echo "--------------------------"
echo "请选择处理方式："
echo "1. 完整流程: eod_processor.py → generate_json_from_eod.py → normalize_eod.py"
echo "2. 仅运行 eod_processor.py"
echo "3. 仅运行 generate_json_from_eod.py"
echo "4. 手动运行其他脚本"
echo "5. 跳过（假设已处理）"
echo ""
read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "运行完整流程..."
        python3 eod_processor.py
        echo ""
        python3 generate_json_from_eod.py
        echo ""
        python3 normalize_eod.py
        ;;
    2) python3 eod_processor.py ;;
    3) python3 generate_json_from_eod.py ;;
    4)
        echo "可用脚本："
        ls *.py | grep -v "__pycache__"
        read -p "请输入脚本名: " script_name
        if [ -f "$script_name" ]; then
            python3 "$script_name"
        else
            echo "❌ 脚本不存在"
        fi
        ;;
    5) echo "跳过EOD处理" ;;
    *) echo "无效选择" ;;
esac

read -p "按Enter继续..."

# 第2部分：检查数据格式
echo -e "\n🔍 第2步：检查数据格式..."
echo "--------------------------"
cd /storage/emulated/0/bursasearch/myx_shop

echo "检查是否有 '=\"数字' 格式问题："
ERROR_COUNT=0

# 检查web目录
if [ -d "web" ]; then
    WEB_ERRORS=$(grep -r '="[0-9]' web/ 2>/dev/null | wc -l)
    if [ "$WEB_ERRORS" -gt 0 ]; then
        echo "  ❌ web/目录: $WEB_ERRORS 处问题"
        ERROR_COUNT=$((ERROR_COUNT + WEB_ERRORS))
    else
        echo "  ✅ web/目录: 正常"
    fi
fi

# 检查data/json目录
if [ -d "data/json" ]; then
    DATA_ERRORS=$(grep -r '="[0-9]' data/json/ 2>/dev/null | wc -l)
    if [ "$DATA_ERRORS" -gt 0 ]; then
        echo "  ❌ data/json/目录: $DATA_ERRORS 处问题"
        ERROR_COUNT=$((ERROR_COUNT + DATA_ERRORS))
    else
        echo "  ✅ data/json/目录: 正常"
    fi
fi

# 检查scripts目录
cd scripts
SCRIPTS_ERRORS=$(grep -r '="[0-9]' *.json 2>/dev/null | wc -l)
if [ "$SCRIPTS_ERRORS" -gt 0 ]; then
    echo "  ❌ scripts/目录: $SCRIPTS_ERRORS 处问题"
    ERROR_COUNT=$((ERROR_COUNT + SCRIPTS_ERRORS))
else
    echo "  ✅ scripts/目录: 正常"
fi

# 第3部分：修复格式问题
echo -e "\n🔧 第3步：修复格式问题..."
echo "--------------------------"
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "发现 $ERROR_COUNT 处格式问题，正在修复..."
    
    # 修复scripts目录下的JSON文件
    for json_file in *.json 2>/dev/null; do
        if [ -f "$json_file" ]; then
            echo "  修复: $json_file"
            sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$json_file"
            sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$json_file"
            sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$json_file"
            sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$json_file"
        fi
    done
    
    # 修复web目录
    cd /storage/emulated/0/bursasearch/myx_shop
    if [ -d "web" ]; then
        for json_file in web/*.json web/history/*.json 2>/dev/null; do
            if [ -f "$json_file" ]; then
                echo "  修复: $json_file"
                sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$json_file"
                sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$json_file"
                sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$json_file"
            fi
        done
    fi
    
    echo "✅ 修复完成"
else
    echo "✅ 未发现格式问题，跳过修复"
fi

# 第4部分：验证6742显示
echo -e "\n✅ 第4步：验证6742显示..."
echo "--------------------------"
cd /storage/emulated/0/bursasearch/myx_shop

echo "检查关键文件中的6742："
for file in web/picks_latest.json scripts/picks_latest.json 2>/dev/null; do
    if [ -f "$file" ]; then
        echo -n "  $(basename $file): "
        if grep -q '="6742"' "$file" 2>/dev/null; then
            echo "❌ 仍有问题"
        elif grep -q '"6742"' "$file" 2>/dev/null; then
            echo "✅ 正常"
        else
            echo "ℹ️  未找到6742"
        fi
    fi
done

# 第5部分：推送到GitHub
echo -e "\n🚀 第5步：推送到GitHub..."
echo "--------------------------"
cd /storage/emulated/0/bursasearch/myx_shop

echo "Git状态："
git status --short 2>/dev/null | head -5

read -p "是否提交并推送？(y/n): " confirm
if [ "$confirm" = "y" ]; then
    git add scripts/*.json web/*.json data/json/*.json 2>/dev/null
    git commit -m "明日EOD更新: $(date '+%Y-%m-%d %H:%M:%S')
- 处理EOD数据
- 检查修复数据格式
- 确保6742显示正常"
    
    echo "正在推送到GitHub..."
    git push
    echo "✅ 推送完成！"
else
    echo "❌ 跳过推送"
fi

# 第6部分：最终提醒
echo -e "\n📱 第6步：手动测试（必须做！）"
echo "--------------------------"
echo "重要：收钱要负责！必须手动测试！"
echo ""
echo "请立即访问："
echo "🌐 https://bursasearch.github.io/myx_shop/"
echo ""
echo "测试项目："
echo "1. 页面能否正常打开"
echo "2. 6742是否显示正常（不是='6742'）"
echo "3. 投资计算器功能是否正常"
echo "4. 支付信息是否正确"
echo ""
echo "⏰ 等待1-2分钟让GitHub更新"
echo "   按 Ctrl+F5 强制刷新"

echo -e "\n🎉 明日流程完成！"
echo "时间: $(date '+%H:%M:%S')"
