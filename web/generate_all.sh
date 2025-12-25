#!/bin/bash
echo "=== 完整的JSON文件生成解决方案 ==="
echo ""

# 1. 检查规范化目录
echo "📁 检查规范化目录..."
if [ ! -d "./normalized_now" ]; then
    echo "❌ 规范化目录不存在"
    echo "请先运行: ./process_directly.sh"
    exit 1
fi

# 2. 找到最新的CSV文件
echo "📊 查找最新的CSV文件..."
latest_csv=$(ls -t ./normalized_now/*.csv 2>/dev/null | head -1)
if [ -z "$latest_csv" ]; then
    echo "❌ 没有找到CSV文件"
    exit 1
fi

echo "   使用: $(basename "$latest_csv")"
echo ""

# 3. 生成JSON文件
echo "🔄 生成JSON文件..."
python3 safe_generate_web_data.py

# 4. 检查生成的文件
echo ""
echo "✅ 生成完成!"
echo ""
echo "📋 生成的文件:"
ls -la web/*.json | awk '{print $9, $5" bytes"}'
echo ""
echo "📱 现在可以:"
echo "   1. 直接在浏览器中打开 retail-inv.html"
echo "   2. 或者运行: python3 start_test_server.py"
echo ""
echo "🔍 验证数据:"
echo "   股票数量: $(python3 -c "import json; d=json.load(open('web/latest_price.json')); print(d['total_stocks'])")"
echo "   推荐数量: $(python3 -c "import json; d=json.load(open('web/picks_latest.json')); print(d['total_picks'])")"
