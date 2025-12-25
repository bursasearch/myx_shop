#!/bin/bash
echo "=== 简单实用的EOD处理脚本 ==="
echo "说明: 这个脚本会处理所有CSV文件，使用数据库和智能推断确定行业"

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_final_simple"
AUDIT_DIR="./audit_final_simple"
CONFIG_FILE="./eod_config.json"

# 创建目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$AUDIT_DIR"

# 显示数据库信息
echo "使用的配置文件: $CONFIG_FILE"
if [ -f "real_sector_database.json" ]; then
    db_count=$(python3 -c "import json; data=json.load(open('real_sector_database.json')); print(len(data))")
    echo "行业数据库记录: $db_count 条"
fi

# 获取文件列表
files=("$INPUT_DIR"/*.csv)
total_files=${#files[@]}
echo "找到 $total_files 个CSV文件"

# 处理文件
processed=0
skipped=0

for input_file in "${files[@]}"; do
    if [ ! -f "$input_file" ]; then
        continue
    fi
    
    filename=$(basename "$input_file" .csv)
    output_file="$OUTPUT_DIR/normalized_$filename.csv"
    audit_file="$AUDIT_DIR/audit_$filename.json"
    
    processed=$((processed + 1))
    echo "[$processed/$total_files] $filename"
    
    # 运行处理脚本
    python3 normalize_eod.py "$input_file" "$output_file" "$CONFIG_FILE" "$audit_file"
    
    # 显示简要结果
    if [ -f "$output_file" ]; then
        total_lines=$(tail -n +2 "$output_file" | wc -l)
        unknown_lines=$(grep -c ",Unknown," "$output_file" 2>/dev/null || echo "0")
        
        if [ "$total_lines" -gt 0 ]; then
            unknown_percent=$((unknown_lines * 100 / total_lines))
            echo "  → $total_lines 行, Unknown: $unknown_percent%"
        fi
    else
        echo "  → 处理失败"
        skipped=$((skipped + 1))
    fi
done

# 生成汇总报告
echo ""
echo "=== 处理完成 ==="
echo "总文件数: $total_files"
echo "成功处理: $((processed - skipped))"
echo "失败: $skipped"
echo "输出目录: $OUTPUT_DIR"

# 生成行业分布报告
if [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
    echo ""
    echo "=== 总体行业分布 ==="
    
    all_sectors_file="overall_sector_distribution.txt"
    > "$all_sectors_file"  # 清空文件
    
    for output_file in "$OUTPUT_DIR"/*.csv; do
        if [ -f "$output_file" ]; then
            tail -n +2 "$output_file" | cut -d',' -f3 >> "temp_sectors.txt"
        fi
    done
    
    if [ -f "temp_sectors.txt" ]; then
        sort "temp_sectors.txt" | uniq -c | sort -rn > "$all_sectors_file"
        rm -f "temp_sectors.txt"
        
        echo "行业分布 (前10名):"
        head -10 "$all_sectors_file"
        
        # 计算Unknown比例
        total=$(awk '{sum+=$1} END{print sum}' "$all_sectors_file" 2>/dev/null || echo "0")
        unknown=$(grep "Unknown" "$all_sectors_file" | awk '{print $1}' 2>/dev/null || echo "0")
        
        if [ "$total" -gt 0 ]; then
            unknown_percent=$((unknown * 100 / total))
            echo ""
            echo "Unknown比例: $unknown_percent% ($unknown/$total)"
            
            if [ $unknown_percent -gt 30 ]; then
                echo "⚠ 建议: 请检查 missing_codes_to_research.txt 并补充行业映射"
            else
                echo "✓ 处理效果良好"
            fi
        fi
        
        echo "完整分布已保存到: $all_sectors_file"
    fi
fi

echo ""
echo "=== 后续建议 ==="
echo "1. 查看 missing_codes_to_research.txt 文件，找到未识别的股票代码"
echo "2. 手动为这些代码添加行业映射到 manual_sector_mapping.json"
echo "3. 重新运行此脚本以应用新的映射"
