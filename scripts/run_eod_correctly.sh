#!/bin/bash
# run_eod_correctly.sh - 支持假期的EOD处理器（修复版）
# 修复问题：
# 1. 日期逻辑错误 - 正确处理EOD数据日期
# 2. 支持假期处理 - 包括周三圣诞节等公共假期
# 3. 智能交易日查找

cd /storage/emulated/0/bursasearch/myx_shop/scripts || {
    echo "❌ 无法切换到脚本目录"
    exit 1
}

# ========== 日期处理函数 ==========

# 获取最近的有效交易日（智能版）
get_trading_date() {
    # 获取YYYYMMDD格式的最近交易日
    local max_lookback=10
    
    echo "🔍 查找最近的有效交易日..."
    
    # 检查是否有手动指定的日期
    if [ -n "$MANUAL_DATE" ]; then
        echo "📅 使用手动指定日期: $MANUAL_DATE"
        echo "$MANUAL_DATE"
        return 0
    fi
    
    # 计算逻辑：从昨天开始往前找
    for ((i=1; i<=max_lookback; i++)); do
        check_date=$(date -d "$i days ago" '+%Y%m%d')
        check_date_display="${check_date:0:4}-${check_date:4:2}-${check_date:6:2}"
        day_of_week=$(date -d "$check_date_display" '+%u')  # 1=周一, 7=周日
        
        # 跳过周末
        if [[ $day_of_week -eq 6 ]] || [[ $day_of_week -eq 7 ]]; then
            echo "  📅 $check_date_display: 周末"
            continue
        fi
        
        # 检查是否是公共假期
        if is_public_holiday "$check_date"; then
            continue
        fi
        
        # 检查是否有对应的数据文件
        if [ -f "history/picks_${check_date}.json" ]; then
            echo "⚠️  $check_date_display: 已有数据文件"
            # 继续往前找更新的日期
            continue
        fi
        
        echo "✅ 找到有效交易日: $check_date_display"
        echo "$check_date"
        return 0
    done
    
    # 如果找不到新的交易日，使用最近有数据的交易日
    echo "⚠️  未找到新的交易日，使用最近有数据的日期"
    get_latest_existing_date
}

# 检查是否是公共假期
is_public_holiday() {
    local date_str="$1"
    local year="${date_str:0:4}"
    local month="${date_str:4:2}"
    local day="${date_str:6:2}"
    local display_date="${year}-${month}-${day}"
    
    # 马来西亚2026年公共假期列表（修复语法）
    declare -A HOLIDAYS_2026=(
        ["20260101"]="元旦"
        ["20260202"]="大宝森节"
        ["20260217"]="农历新年"
        ["20260307"]="可兰经降世日"
        ["20260321"]="开斋节"
        ["20260322"]="开斋节第二天"
        ["20260501"]="劳动节"
        ["20260502"]="卫塞节补假"
        ["20260601"]="国家元首诞辰"
        ["20260617"]="回历新年"
        ["20260825"]="真主圣诞"
        ["20260831"]="国庆日"
        ["20260916"]="马来西亚日"
        ["20261108"]="屠妖节"
        ["20261225"]="圣诞节"  # 周四
    )
    
    if [[ -n "${HOLIDAYS_2026[$date_str]}" ]]; then
        echo "  📅 $display_date: ${HOLIDAYS_2026[$date_str]}"
        return 0  # 是假期
    fi
    
    return 1  # 不是假期
}

# 获取最近已有数据的日期
get_latest_existing_date() {
    if ls history/picks_*.json 1>/dev/null 2>&1; then
        latest_file=$(ls history/picks_*.json | sort -r | head -1)
        latest_date=$(basename "$latest_file" | sed 's/picks_\(.*\)\.json/\1/')
        echo "📊 使用最近数据日期: ${latest_date:0:4}-${latest_date:4:2}-${latest_date:6:2}"
        echo "$latest_date"
        return 0
    else
        echo "❌ 没有找到历史数据文件"
        # 使用昨天作为默认
        default_date=$(date -d "yesterday" '+%Y%m%d')
        echo "📊 使用默认日期: ${default_date:0:4}-${default_date:4:2}-${default_date:6:2}"
        echo "$default_date"
        return 0
    fi
}

# ========== 选项函数 ==========

# 选项1：处理EOD数据
option1() {
    echo "📊 处理EOD数据..."
    echo "========================"
    
    # 获取正确的交易日期
    DATA_DATE=$(get_trading_date)
    TODAY_DATE=$(date '+%Y%m%d')
    
    echo ""
    echo "📅 今天日期: $(date '+%Y-%m-%d %A')"
    echo "📊 数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"
    echo ""
    
    # 生成JSON
    echo "1. 生成JSON数据..."
    echo "----------------"
    
    # 检查Python脚本是否存在
    if [ ! -f "generate_json_from_eod.py" ]; then
        echo "❌ 找不到 generate_json_from_eod.py"
        return 1
    fi
    
    # 运行Python脚本，传递日期参数
    python3 generate_json_from_eod.py --date "$DATA_DATE"
    if [ $? -ne 0 ]; then
        echo "❌ Python脚本执行失败"
        return 1
    fi
    
    # 创建历史文件
    echo ""
    echo "2. 创建历史文件..."
    echo "----------------"
    
    mkdir -p history
    mkdir -p ../web/history
    
    if [ -f "picks_latest.json" ]; then
        # 复制为历史文件
        cp picks_latest.json "history/picks_${DATA_DATE}.json"
        echo "✅ 创建历史文件: picks_${DATA_DATE}.json"
        
        # 检查文件大小
        file_size=$(wc -c < "history/picks_${DATA_DATE}.json")
        if [ "$file_size" -lt 100 ]; then
            echo "⚠️  警告: 历史文件可能为空或太小 ($file_size bytes)"
        fi
    else
        echo "⚠️  picks_latest.json 不存在，跳过历史文件创建"
    fi
    
    # 复制到web目录
    echo ""
    echo "3. 复制到web目录..."
    echo "----------------"
    
    mkdir -p ../web
    
    copy_count=0
    if [ -f "picks_latest.json" ]; then
        cp picks_latest.json ../web/ 2>/dev/null && echo "✅ picks_latest.json" && ((copy_count++))
    fi
    
    if [ -f "latest_price.json" ]; then
        cp latest_price.json ../web/ 2>/dev/null && echo "✅ latest_price.json" && ((copy_count++))
    fi
    
    if [ -f "data.json" ]; then
        cp data.json ../web/ 2>/dev/null && echo "✅ data.json" && ((copy_count++))
    fi
    
    # 复制历史文件
    if [ -f "history/picks_${DATA_DATE}.json" ]; then
        cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null && \
            echo "✅ picks_${DATA_DATE}.json (历史)" && ((copy_count++))
    fi
    
    if [ $copy_count -eq 0 ]; then
        echo "⚠️  没有复制任何文件"
    fi
    
    echo ""
    echo "🎉 处理完成！"
    echo "✅ 数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"
    echo "✅ 处理时间: $(date '+%H:%M:%S')"
}

# 选项2：修复股票代码格式（保持不变）
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
import glob
for pattern in ["history/*.json", "../web/history/*.json"]:
    for file in glob.glob(pattern):
        fixed = fix_file(file)
        if fixed > 0:
            print(f"✅ {file}: 修复了 {fixed} 个代码")
PYCODE
    
    python3 fix_codes.py
    rm -f fix_codes.py 2>/dev/null
    
    echo ""
    echo "✅ 修复完成！"
}

# 选项3：同步日期选择器
option3() {
    echo "🔄 同步日期选择器..."
    echo "------------------"
    
    cd /storage/emulated/0/bursasearch/myx_shop || {
        echo "❌ 无法切换到web目录"
        return 1
    }
    
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
    
    # 排序（按日期从早到晚）
    IFS=$'\n' sorted=($(sort <<<"${DATES[*]}"))
    unset IFS
    
    echo "找到 ${#sorted[@]} 个历史日期"
    
    # 生成JS文件
    cat > web/date_config.js << 'JS'
// 可用日期列表 - 自动生成
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

// 获取日期显示名称
function getDateDisplay(dateId) {
    if (!dateId || dateId.length !== 8) return dateId;
    return dateId.substring(0,4) + '-' + dateId.substring(4,6) + '-' + dateId.substring(6,8);
}

console.log('日期配置已加载，共有 ' + window.availableDates.length + ' 个可用日期');
JS
    
    echo "✅ 已生成: web/date_config.js"
    
    # 检查HTML
    if [ -f "web/retail-inv.html" ]; then
        if grep -q "date_config.js" "web/retail-inv.html"; then
            echo "✅ HTML已引用 date_config.js"
        else
            echo "⚠️ 请在HTML中添加: <script src='date_config.js'></script>"
            echo "   添加位置: 在</body>标签之前"
        fi
    fi
    
    echo ""
    echo "最近5个日期:"
    for date in "${sorted[@]: -5}"; do
        echo "  ${date:0:4}-${date:4:2}-${date:6:2}"
    done
}

# 选项4：查看状态
option4() {
    echo "📁 文件状态..."
    echo "-------------"
    
    echo "📂 scripts目录:"
    for file in picks_latest.json latest_price.json data.json; do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file" 2>/dev/null || echo "0")
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            modified=$(date -r "$file" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "未知")
            echo "  📄 $file"
            echo "     大小: $size bytes, 行数: $lines, 修改: $modified"
        else
            echo "  ❌ $file (不存在)"
        fi
    done
    
    echo ""
    echo "📂 history目录:"
    hist_files=($(ls history/*.json 2>/dev/null))
    hist_count=${#hist_files[@]}
    echo "  文件数量: $hist_count"
    
    if [ $hist_count -gt 0 ]; then
        latest_hist=$(ls -t history/*.json | head -1)
        latest_date=$(basename "$latest_hist" | sed 's/picks_\(.*\)\.json/\1/')
        echo "  最新文件: picks_${latest_date}.json"
        echo "  日期范围:"
        first_file=$(ls history/*.json | head -1)
        first_date=$(basename "$first_file" | sed 's/picks_\(.*\)\.json/\1/')
        echo "    最早: ${first_date:0:4}-${first_date:4:2}-${first_date:6:2}"
        echo "    最新: ${latest_date:0:4}-${latest_date:4:2}-${latest_date:6:2}"
    fi
    
    echo ""
    echo "📂 web目录:"
    if [ -d "../web" ]; then
        web_count=$(ls ../web/*.json 2>/dev/null | wc -l)
        web_hist_count=$(ls ../web/history/*.json 2>/dev/null 2>/dev/null | wc -l)
        echo "  JSON文件: $web_count 个"
        echo "  历史文件: $web_hist_count 个"
    else
        echo "  ❌ web目录不存在"
    fi
    
    echo ""
    echo "📅 系统信息:"
    echo "  当前时间: $(date '+%Y-%m-%d %H:%M:%S %A')"
    echo "  数据日期: $(get_latest_existing_date | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')"
}

# 选项5：手动指定日期处理
option5() {
    echo "📅 手动指定日期..."
    echo "----------------"
    echo "当前自动找到的日期: $(get_trading_date)"
    echo ""
    echo "请输入日期 (格式: YYYYMMDD, 例如: 20261224)"
    echo "或按回车键使用自动检测的日期"
    read -p "日期: " manual_date
    
    if [ -n "$manual_date" ]; then
        # 验证日期格式
        if [[ ! "$manual_date" =~ ^[0-9]{8}$ ]]; then
            echo "❌ 日期格式错误，必须为YYYYMMDD"
            return
        fi
        
        # 验证是否是有效日期
        if ! date -d "${manual_date:0:4}-${manual_date:4:2}-${manual_date:6:2}" >/dev/null 2>&1; then
            echo "❌ 无效日期"
            return
        fi
        
        echo "✅ 将使用手动指定日期: $manual_date"
        export MANUAL_DATE="$manual_date"
        option1
        unset MANUAL_DATE
    else
        echo "使用自动检测日期"
        option1
    fi
}

# 显示菜单
show_menu() {
    clear
    echo "========================================"
    echo "    🚀 EOD处理器 假期修复版"
    echo "========================================"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S %A')"
    echo "目录: $(pwd)"
    echo ""
    
    # 显示当前状态
    if [ -f "picks_latest.json" ]; then
        latest_date=$(get_latest_existing_date)
        echo "📊 当前数据: ${latest_date:0:4}-${latest_date:4:2}-${latest_date:6:2}"
    fi
    
    echo ""
    echo "请选择操作："
    echo "1. 处理EOD数据（生成JSON）"
    echo "2. 修复股票代码格式"
    echo "3. 同步日期选择器"
    echo "4. 查看文件状态"
    echo "5. 手动指定日期处理"
    echo "6. 退出"
    echo ""
    read -p "请输入选择 (1-6): " choice
    echo ""
}

# ========== 主程序 ==========

# 检查Python
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要Python3，请先安装"
    exit 1
fi

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
            option5
            ;;
        6)
            echo "👋 再见！"
            echo "========================================"
            exit 0
            ;;
        *)
            echo "❌ 无效选择，请输入1-6"
            ;;
    esac
    
    echo ""
    echo "========================================"
    read -p "按回车键继续..." dummy
done