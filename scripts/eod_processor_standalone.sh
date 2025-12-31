#!/bin/bash
# 独立EOD处理器 - 自动检测和生成所有必要文件

echo "🔧 独立EOD处理器 v1.0"
echo "====================="

# 配置
EOD_SOURCE_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
WORK_DIR="/storage/emulated/0/bursasearch/myx_shop/scripts"
WEB_DIR="$WORK_DIR/../web"

# 检查目录
check_dirs() {
    echo "📁 检查目录..."
    
    if [ ! -d "$EOD_SOURCE_DIR" ]; then
        echo "❌ EOD源目录不存在: $EOD_SOURCE_DIR"
        return 1
    fi
    echo "✅ EOD源目录: $EOD_SOURCE_DIR"
    
    if [ ! -d "$WORK_DIR" ]; then
        echo "❌ 工作目录不存在: $WORK_DIR"
        return 1
    fi
    echo "✅ 工作目录: $WORK_DIR"
    
    return 0
}

# 查找最新的EOD文件
find_latest_eod() {
    echo ""
    echo "🔍 查找最新EOD文件..."
    
    # 按修改时间排序，取最新的CSV文件
    LATEST_CSV=$(find "$EOD_SOURCE_DIR" -name "*.csv" -type f 2>/dev/null | sort -r | head -1)
    
    if [ -z "$LATEST_CSV" ]; then
        echo "❌ 在 $EOD_SOURCE_DIR 中找不到CSV文件"
        return 1
    fi
    
    echo "✅ 找到最新文件: $(basename "$LATEST_CSV")"
    echo "📊 文件大小: $(wc -c < "$LATEST_CSV" 2>/dev/null || echo "未知") bytes"
    echo "📅 修改时间: $(date -r "$LATEST_CSV" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "未知")"
    
    echo "$LATEST_CSV"
    return 0
}

# 智能日期提取
extract_date_intelligent() {
    local filename="$1"
    local basename=$(basename "$filename" .csv)
    
    echo ""
    echo "📅 从文件名提取日期: $basename"
    
    # 移除常见前缀
    clean_name=$(echo "$basename" | sed 's/^eod_//i; s/^EOD_//i; s/^myx_//i; s/^bursa_//i')
    
    # 尝试多种模式
    declare -A patterns=(
        ["YYYYMMDD"]='^([0-9]{4})([0-9]{2})([0-9]{2})$'
        ["YYMMDD"]='^([0-9]{2})([0-9]{2})([0-9]{2})$'
        ["YYYY-MM-DD"]='([0-9]{4})-([0-9]{2})-([0-9]{2})'
        ["YYYY_MM_DD"]='([0-9]{4})_([0-9]{2})_([0-9]{2})'
    )
    
    for pattern_name in "${!patterns[@]}"; do
        pattern="${patterns[$pattern_name]}"
        
        if [[ "$clean_name" =~ $pattern ]]; then
            case "$pattern_name" in
                "YYYYMMDD")
                    year="${BASH_REMATCH[1]}"
                    month="${BASH_REMATCH[2]}"
                    day="${BASH_REMATCH[3]}"
                    ;;
                "YYMMDD")
                    yy="${BASH_REMATCH[1]}"
                    month="${BASH_REMATCH[2]}"
                    day="${BASH_REMATCH[3]}"
                    
                    # 智能判断世纪
                    if [ "$yy" -ge 25 ] && [ "$yy" -le 99 ]; then
                        year="20${yy}"
                    elif [ "$yy" -ge 0 ] && [ "$yy" -le 24 ]; then
                        year="20${yy}"
                    else
                        continue  # 跳过无效的年份
                    fi
                    ;;
                "YYYY-MM-DD"|"YYYY_MM_DD")
                    year="${BASH_REMATCH[1]}"
                    month="${BASH_REMATCH[2]}"
                    day="${BASH_REMATCH[3]}"
                    ;;
            esac
            
            # 验证日期合理性
            if [[ "$month" =~ ^(0[1-9]|1[0-2])$ ]] && [[ "$day" =~ ^(0[1-9]|[12][0-9]|3[01])$ ]]; then
                if [ "$year" -ge 2000 ] && [ "$year" -le 2100 ]; then
                    date_str="${year}${month}${day}"
                    echo "✅ 使用模式 '$pattern_name': $date_str"
                    echo "$date_str"
                    return 0
                fi
            fi
        fi
    done
    
    # 如果无法提取，使用文件修改日期
    file_date=$(date -r "$filename" '+%Y%m%d' 2>/dev/null || date '+%Y%m%d')
    echo "⚠️  无法从文件名提取日期，使用文件修改日期: $file_date"
    echo "$file_date"
    return 0
}

# 处理EOD文件
process_eod_file() {
    local csv_file="$1"
    local data_date="$2"
    
    echo ""
    echo "🚀 开始处理EOD数据..."
    echo "📁 源文件: $(basename "$csv_file")"
    echo "📅 数据日期: ${data_date:0:4}-${data_date:4:2}-${data_date:6:2}"
    
    # 切换到工作目录
    cd "$WORK_DIR" || return 1
    
    # 复制CSV文件到工作目录
    cp "$csv_file" .
    local working_csv=$(basename "$csv_file")
    
    # 检查Python脚本
    if [ ! -f "generate_json_from_eod.py" ]; then
        echo "❌ 找不到 generate_json_from_eod.py"
        return 1
    fi
    
    # 运行Python脚本
    echo ""
    echo "▶️  运行Python脚本..."
    python3 generate_json_from_eod.py "$working_csv"
    
    if [ $? -ne 0 ]; then
        echo "❌ Python脚本执行失败"
        return 1
    fi
    
    # 确保所有必要的JSON文件都生成
    echo ""
    echo "📁 检查生成的文件..."
    
    required_files=("picks_latest.json" "latest_price.json" "data.json")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file")
            echo "✅ $file ($size bytes)"
        else
            echo "❌ $file (缺失)"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo "⚠️  缺失文件: ${missing_files[*]}"
    fi
    
    # 创建目录结构
    mkdir -p history
    mkdir -p "$WEB_DIR/history"
    
    # 生成历史文件（如果picks_latest.json存在）
    if [ -f "picks_latest.json" ]; then
        hist_file="history/picks_${data_date}.json"
        cp picks_latest.json "$hist_file"
        echo "✅ 历史文件: $hist_file"
    fi
    
    # 复制到web目录
    echo ""
    echo "🌐 复制到web目录..."
    
    copy_to_web() {
        local src="$1"
        local dst="$2"
        
        if [ -f "$src" ]; then
            cp "$src" "$dst" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ $(basename "$src") → web/"
                return 0
            else
                echo "❌ 无法复制 $(basename "$src")"
                return 1
            fi
        fi
        return 1
    }
    
    copy_count=0
    copy_to_web "picks_latest.json" "$WEB_DIR/" && ((copy_count++))
    copy_to_web "latest_price.json" "$WEB_DIR/" && ((copy_count++))
    copy_to_web "data.json" "$WEB_DIR/" && ((copy_count++))
    
    if [ -f "history/picks_${data_date}.json" ]; then
        copy_to_web "history/picks_${data_date}.json" "$WEB_DIR/history/" && ((copy_count++))
    fi
    
    echo "📋 共复制 $copy_count 个文件到web目录"
    
    return 0
}

# 主函数
main() {
    echo "⏰ 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 检查目录
    if ! check_dirs; then
        exit 1
    fi
    
    # 查找最新EOD文件
    CSV_FILE=$(find_latest_eod)
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # 提取日期
    DATA_DATE=$(extract_date_intelligent "$CSV_FILE")
    
    # 让用户确认
    echo ""
    echo "📋 处理摘要:"
    echo "  文件: $(basename "$CSV_FILE")"
    echo "  日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"
    echo ""
    
    read -p "是否继续处理? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "操作取消"
        exit 0
    fi
    
    # 处理文件
    if process_eod_file "$CSV_FILE" "$DATA_DATE"; then
        echo ""
        echo "========================================"
        echo "🎉 EOD处理完成！"
        echo "📅 数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"
        echo "⏰ 完成时间: $(date '+%H:%M:%S')"
        echo ""
        
        # 显示最终文件状态
        echo "📁 最终文件状态:"
        echo "工作目录 ($WORK_DIR):"
        ls -la *.json 2>/dev/null | grep -E "(picks|price|data)\.json" || echo "  无JSON文件"
        
        echo ""
        echo "历史目录:"
        ls -la history/picks_*.json 2>/dev/null | tail -3 || echo "  无历史文件"
        
        echo ""
        echo "Web目录 ($WEB_DIR):"
        ls -la "$WEB_DIR"/*.json 2>/dev/null | grep -E "(picks|price|data)\.json" || echo "  无JSON文件"
    else
        echo "❌ 处理失败"
        exit 1
    fi
}

# 运行主函数
main "$@"
