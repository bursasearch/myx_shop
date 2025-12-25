#!/bin/bash
echo "=== 工作版批量处理脚本 ==="

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_working"
CONFIG_FILE="./eod_config.json"

# 创建目录
mkdir -p "$OUTPUT_DIR"

# 显示信息
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "配置文件: $CONFIG_FILE"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在"
    exit 1
fi

# 验证配置文件
echo -n "验证配置文件... "
python3 -c "
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    print('✓ 有效')
    print(f'   Schema列: {len(config.get(\"schema\", []))}')
    print(f'   Sector映射: {len(config.get(\"sector_lookup\", {}))}')
except Exception as e:
    print(f'✗ 无效: {e}')
    exit(1)
"

# 获取文件列表
files=($(ls "$INPUT_DIR"/*.csv 2>/dev/null | sort))
total_files=${#files[@]}

if [ $total_files -eq 0 ]; then
    echo "错误: 在 $INPUT_DIR 中没有找到CSV文件"
    exit 1
fi

echo ""
echo "找到 $total_files 个CSV文件"
echo "开始处理..."

# 处理统计
success=0
failed=0
total_rows=0
sector_stats_file="sector_final_stats.txt"
> "$sector_stats_file"

# 处理每个文件
for input_file in "${files[@]}"; do
    filename=$(basename "$input_file" .csv)
    output_file="$OUTPUT_DIR/normalized_$filename.csv"
    
    echo -n "处理 $filename ... "
    
    # 运行处理脚本
    python3 normalize_eod_simple.py "$input_file" "$output_file" "$CONFIG_FILE" > /tmp/process_$filename.log 2>&1
    
    if [ $? -eq 0 ] && [ -f "$output_file" ] && [ -s "$output_file" ]; then
        # 统计信息
        rows=$(tail -n +2 "$output_file" | wc -l)
        total_rows=$((total_rows + rows))
        
        # 收集Sector统计
        tail -n +2 "$output_file" | cut -d',' -f3 >> "/tmp/all_sectors.txt"
        
        # 计算Unknown比例
        unknown=$(grep -c ",Unknown," "$output_file" 2>/dev/null || echo "0")
        if [ $rows -gt 0 ]; then
            unknown_percent=$((unknown * 100 / rows))
            echo "✓ $rows 行, Unknown: $unknown_percent%"
        else
            echo "✓ $rows 行"
        fi
        
        success=$((success + 1))
    else
        echo "✗ 失败"
        failed=$((failed + 1))
        
        # 显示错误
        if [ -f "/tmp/process_$filename.log" ]; then
            echo "  错误: $(tail -1 "/tmp/process_$filename.log")"
        fi
    fi
done

# 总体统计
echo ""
echo "=== 处理完成 ==="
echo "成功: $success/$total_files"
echo "失败: $failed/$total_files"
echo "总行数: $total_rows"

# 生成Sector统计
if [ -f "/tmp/all_sectors.txt" ]; then
    echo ""
    echo "=== 总体Sector分布 ==="
    
    sort "/tmp/all_sectors.txt" | uniq -c | sort -rn > "$sector_stats_file"
    
    echo "前10名行业:"
    head -10 "$sector_stats_file"
    
    # 计算Unknown比例
    total_sectors=$(wc -l < "/tmp/all_sectors.txt")
    unknown_sectors=$(grep -c "^Unknown$" "/tmp/all_sectors.txt" || echo "0")
    
    if [ $total_sectors -gt 0 ]; then
        unknown_percent=$((unknown_sectors * 100 / total_sectors))
        echo ""
        echo "Unknown比例: $unknown_percent% ($unknown_sectors/$total_sectors)"
        
        if [ $unknown_percent -lt 10 ]; then
            echo "✓ 优秀！超过90%的Sector已正确映射"
        elif [ $unknown_percent -lt 20 ]; then
            echo "✓ 良好！超过80%的Sector已正确映射"
        elif [ $unknown_percent -lt 30 ]; then
            echo "⚠ 一般！约70%的Sector已正确映射"
        else
            echo "⚠ 需要改进！Unknown比例较高"
        fi
    fi
    
    rm -f "/tmp/all_sectors.txt"
fi

# 显示示例
echo ""
echo "=== 示例输出 ==="
sample_output=$(ls "$OUTPUT_DIR"/normalized_*.csv 2>/dev/null | head -1)
if [ -f "$sample_output" ]; then
    sample_name=$(basename "$sample_output")
    echo "文件: $sample_name"
    echo ""
    echo "标题行:"
    head -1 "$sample_output" | sed 's/,/ | /g'
    echo ""
    echo "前3行数据:"
    head -4 "$sample_output" | tail -3 | while read line; do
        echo "$line" | sed 's/,/ | /g'
    done
fi

echo ""
echo "=== 输出信息 ==="
echo "处理后的文件: $OUTPUT_DIR/"
echo "Sector统计: $sector_stats_file"
echo ""
echo "=== 验证命令 ==="
echo "查看某个文件: column -t -s, $OUTPUT_DIR/normalized_20251223.csv | head -10"
echo "统计Sector: cat $OUTPUT_DIR/*.csv | tail -n +2 | cut -d',' -f3 | sort | uniq -c | sort -rn"
