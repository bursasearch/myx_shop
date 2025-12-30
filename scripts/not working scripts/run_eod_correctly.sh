#!/bin/bash
# run_eod_simple.sh - 简洁可靠的EOD处理器

cd /storage/emulated/0/bursasearch/myx_shop/scripts

# 显示菜单
show_menu() {
    echo "========================================"
    echo "    🚀 EOD处理器 简洁版"
    echo "========================================"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "请选择操作："
    echo "1. 处理EOD数据（生成JSON）"
    echo "2. 修复股票代码格式"
    echo "3. 同步日期选择器"
    echo "4. 查看文件状态"
    echo "5. 退出"
    echo ""
    read -p "请输入选择 (1-5): " choice
    echo ""
}

# 选项1：处理EOD数据
option1() {
    echo "📊 处理EOD数据..."
    echo "----------------"
    
    # 生成JSON
    echo "1. 生成JSON数据..."
    python3 generate_json_from_eod.py
    
    # 修复历史文件名
    echo ""
    echo "2. 修复历史文件名..."
    python3 -c "
import os
from datetime import datetime, timedelta

history_dir = 'history'
if os.path.exists(history_dir):
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    today = datetime.now().strftime('%Y%m%d')
    
    wrong = os.path.join(history_dir, f'picks_{today}.json')
    right = os.path.join(history_dir, f'picks_{yesterday}.json')
    
    if os.path.exists(wrong):
        os.rename(wrong, right)
        print(f'✅ 重命名: picks_{today}.json → picks_{yesterday}.json')
    "
    
    # 复制文件
    echo ""
    echo "3. 复制到web目录..."
    mkdir -p ../web
    mkdir -p ../web/history
    
    if [ -f "picks_latest.json" ]; then
        cp picks_latest.json ../web/ && echo "✅ picks_latest.json"
    fi
    
    if [ -f "latest_price.json" ]; then
        cp latest_price.json ../web/ && echo "✅ latest_price.json"
    fi
    
    if [ -f "data.json" ]; then
        cp data.json ../web/ && echo "✅ data.json"
    fi
    
    if ls history/*.json 1>/dev/null 2>&1; then
        cp history/*.json ../web/history/ && echo "✅ 历史文件"
    fi
    
    echo ""
    echo "🎉 处理完成！"
}

# 选项2：修复股票代码
option2() {
    echo "🔧 修复股票代码格式..."
    echo "-------------------"
    
    # 创建修复脚本
    cat > fix_codes.py << 'PYCODE'
import json, os, re

def fix_file(filepath):
    if not os.path.exists(filepath):
        return 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取失败 {filepath}: {e}")
        return 0
    
    fixed = 0
    
    def fix(obj):
        nonlocal fixed
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if isinstance(value, str):
                    if key.lower() in ['code', 'stock_code', 'ticker']:
                        original = value
                        # 修复格式
                        new_value = re.sub(r'^[=\"]+', '', value)
                        new_value = re.sub(r'[\"]+$', '', new_value)
                        if new_value != original:
                            obj[key] = new_value
                            fixed += 1
                            if fixed <= 3:  # 只显示前3个
                                print(f"  {original} → {new_value}")
                elif isinstance(value, (dict, list)):
                    fix(value)
        elif isinstance(obj, list):
            for item in obj:
                fix(item)
    
    fix(data)
    
    if fixed > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return fixed

# 修复scripts目录
print("修复scripts目录:")
for f in ["picks_latest.json", "latest_price.json", "data.json"]:
    if os.path.exists(f):
        fixed = fix_file(f)
        if fixed > 0:
            print(f"✅ {f}: 修复了 {fixed} 个代码")

# 修复web目录
print("\n修复web目录:")
for f in ["../web/picks_latest.json", "../web/latest_price.json", "../web/data.json"]:
    if os.path.exists(f):
        fixed = fix_file(f)
        if fixed > 0:
            print(f"✅ {f}: 修复了 {fixed} 个代码")

# 修复历史文件
print("\n修复历史文件:")
for f in ["history/*.json", "../web/history/*.json"]:
    import glob
    for file in glob.glob(f):
        fixed = fix_file(file)
        if fixed > 0:
            print(f"✅ {file}: 修复了 {fixed} 个代码")
PYCODE
    
    python3 fix_codes.py
    rm -f fix_codes.py 2>/dev/null
    
    echo ""
    echo "✅ 修复完成！"
}

# 选项3：同步日期
option3() {
    echo "🔄 同步日期选择器..."
    echo "------------------"
    
    cd /storage/emulated/0/bursasearch/myx_shop
    
    # 获取所有日期
    DATES=()
    for file in web/history/picks_*.json; do
        if [ -f "$file" ]; then
            DATE=$(basename "$file" | sed 's/picks_\(.*\)\.json/\1/')
            DATES+=("$DATE")
        fi
    done
    
    if [ ${#DATES[@]} -eq 0 ]; then
        echo "⚠️ 没有找到历史文件"
        echo "请先运行选项1生成数据"
        return
    fi
    
    # 排序
    IFS=$'\n' sorted=($(sort <<<"${DATES[*]}"))
    unset IFS
    
    echo "找到 ${#sorted[@]} 个历史日期"
    
    # 生成JS文件
    cat > web/date_config.js << 'JS'
// 可用日期列表
window.availableDates = [
JS
    
    for date in "${sorted[@]}"; do
        year=${date:0:4}
        month=${date:4:2}
        day=${date:6:2}
        echo "  {id: '$date', display: '$year-$month-$day', file: 'history/picks_$date.json'}," >> web/date_config.js
    done
    
    cat >> web/date_config.js << 'JS'
];

// 默认选中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[window.availableDates.length - 1].id;
}
JS
    
    echo "✅ 已生成: web/date_config.js"
    
    # 检查HTML
    if [ -f "web/retail-inv.html" ]; then
        if grep -q "date_config.js" "web/retail-inv.html"; then
            echo "✅ HTML已引用 date_config.js"
        else
            echo "⚠️ 请在HTML中添加: <script src='date_config.js'></script>"
        fi
    fi
    
    echo ""
    echo "最近日期: ${sorted[*]: -5}"
}

# 选项4：查看状态
option4() {
    echo "📁 文件状态..."
    echo "-------------"
    
    echo "主要文件:"
    for file in picks_latest.json latest_price.json data.json; do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file" 2>/dev/null || echo "N/A")
            echo "  📄 $file ($size bytes)"
        fi
    done
    
    echo ""
    echo "历史文件:"
    hist_count=$(ls history/*.json 2>/dev/null | wc -l)
    echo "  scripts/history: $hist_count 个文件"
    
    echo ""
    echo "web目录:"
    web_count=$(ls ../web/*.json 2>/dev/null | wc -l)
    echo "  web/*.json: $web_count 个文件"
}

# 主循环
while true; do
    show_menu
    
    case $choice in
        1)
            option1
            ;;
        2)
            option2
            ;;
        3)
            option3
            ;;
        4)
            option4
            ;;
        5)
            echo "👋 再见！"
            echo "========================================"
            exit 0
            ;;
        *)
            echo "❌ 无效选择"
            ;;
    esac
    
    echo ""
    echo "========================================"
    read -p "按回车键继续..." dummy
done
