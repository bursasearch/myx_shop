#!/bin/bash
echo "=== 立即开始处理所有文件 ==="

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_now"
CONFIG_FILE="./eod_config.json"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "输入: $INPUT_DIR"
echo "输出: $OUTPUT_DIR"
echo "配置: $CONFIG_FILE"
echo ""

# 获取所有CSV文件
echo "查找文件..."
csv_files=($(find "$INPUT_DIR" -name "*.csv" -type f | sort))

if [ ${#csv_files[@]} -eq 0 ]; then
    echo "错误: 没有找到CSV文件"
    exit 1
fi

echo "找到 ${#csv_files[@]} 个文件"
echo "开始处理..."
echo ""

# 处理每个文件
count=0
success_count=0

for input_file in "${csv_files[@]}"; do
    count=$((count + 1))
    filename=$(basename "$input_file" .csv)
    output_file="$OUTPUT_DIR/normalized_$filename.csv"
    
    echo -n "[$count/${#csv_files[@]}] $filename: "
    
    # 直接调用Python脚本
    python_output=$(python3 normalize_eod_simple.py "$input_file" "$output_file" "$CONFIG_FILE" 2>&1)
    return_code=$?
    
    if [ $return_code -eq 0 ] && [ -f "$output_file" ]; then
        # 检查文件是否有内容
        if [ -s "$output_file" ]; then
            rows=$(tail -n +2 "$output_file" | wc -l)
            echo "✓ $rows 行"
            success_count=$((success_count + 1))
        else
            echo "✗ 输出文件为空"
            rm -f "$output_file"
        fi
    else
        echo "✗ 失败"
        # 显示错误信息
        if [ -n "$python_output" ]; then
            error_line=$(echo "$python_output" | grep -i "error\|fail\|异常" | head -1)
            if [ -n "$error_line" ]; then
                echo "  原因: $error_line"
            fi
        fi
    fi
done

echo ""
echo "=== 处理完成 ==="
echo "总文件数: ${#csv_files[@]}"
echo "成功: $success_count"
echo "失败: $((count - success_count))"

# 显示一些统计信息
if [ $success_count -gt 0 ]; then
    echo ""
    echo "=== 结果检查 ==="
    
    # 找一个成功的文件显示示例
    sample_file=$(ls -t "$OUTPUT_DIR"/*.csv 2>/dev/null | head -1)
    if [ -f "$sample_file" ]; then
        echo "示例文件: $(basename "$sample_file")"
        echo "行数: $(wc -l < "$sample_file")"
        
        echo ""
        echo "前2行数据:"
        head -3 "$sample_file" | column -t -s, | head -3
        
        echo ""
        echo "Sector分布:"
        tail -n +2 "$sample_file" | cut -d',' -f3 | sort | uniq -c | sort -rn | head -5
    fi
    
    # 生成总体统计
    echo ""
    echo "=== 总体统计 ==="
    temp_stats="/tmp/all_sectors_stats.txt"
    > "$temp_stats"
    
    for csv in "$OUTPUT_DIR"/*.csv; do
        if [ -f "$csv" ]; then
                tail -n +2 "$csv" | cut -d',' -f3 >> "$temp_stats" 2>/dev/null || true
        fi
    done
    
    if [ -s "$temp_stats" ]; then
        echo "所有文件的行业分布:"
        sort "$temp_stats" | uniq -c | sort -rn > "final_sector_distribution.txt"
        head -10 "final_sector_distribution.txt"
        
        total=$(wc -l < "$temp_stats")
        unknown=$(grep -c "^Unknown$" "$temp_stats" 2>/dev/null || echo "0")
        if [ $total -gt 0 ]; then
            unknown_percent=$((unknown * 100 / total))
            echo ""
            echo "Unknown比例: $unknown_percent% ($unknown/$total)"
        fi
        
        rm -f "$temp_stats"
    fi
fi

echo ""
echo "输出目录: $OUTPUT_DIR"
echo "行业分布文件: final_sector_distribution.txt"
