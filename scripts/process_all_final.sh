#!/bin/bash
echo "=== 最终版：处理所有EOD文件（使用Sector代码映射）==="
echo "说明：此脚本将数字Sector代码转换为可读的行业名称"

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_with_sector_names"
AUDIT_DIR="./audit_with_sector_names"
CONFIG_FILE="./eod_config.json"

# 创建目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$AUDIT_DIR"

# 显示配置信息
echo "配置文件: $CONFIG_FILE"
if [ -f "sector_code_to_name.json" ]; then
    map_count=$(python3 -c "import json; data=json.load(open('sector_code_to_name.json')); print(len(data['mapping']))")
    echo "Sector代码映射: $map_count 条"
fi

# 获取文件列表
files=("$INPUT_DIR"/*.csv)
total_files=${#files[@]}
echo "找到 $total_files 个CSV文件"
echo ""

# 处理计数器
processed=0
total_rows=0
sector_stats_file="sector_name_distribution.txt"
> "$sector_stats_file"  # 清空文件

# 处理每个文件
for input_file in "${files[@]}"; do
    if [ ! -f "$input_file" ]; then
        continue
    fi
    
    filename=$(basename "$input_file" .csv)
    output_file="$OUTPUT_DIR/normalized_$filename.csv"
    audit_file="$AUDIT_DIR/audit_$filename.json"
    
    processed=$((processed + 1))
    echo -n "[$processed/$total_files] $filename: "
    
    # 运行处理脚本
    python3 normalize_eod.py "$input_file" "$output_file" "$CONFIG_FILE" "$audit_file" 2>/dev/null
    
    if [ -f "$output_file" ] && [ -s "$output_file" ]; then
        # 统计行数
        file_rows=$(tail -n +2 "$output_file" | wc -l)
        total_rows=$((total_rows + file_rows))
        
        # 统计Sector分布
        tail -n +2 "$output_file" | cut -d',' -f3 >> "temp_all_sectors.txt"
        
        # 统计Unknown
        unknown_count=$(grep -c ",Unknown," "$output_file" 2>/dev/null || echo "0")
        if [ "$file_rows" -gt 0 ]; then
            unknown_percent=$((unknown_count * 100 / file_rows))
            echo "$file_rows 行, Unknown: $unknown_percent%"
        else
            echo "0 行"
        fi
    else
        echo "处理失败"
    fi
done

# 生成总体统计
echo ""
echo "=== 总体统计 ==="
echo "处理文件: $processed/$total_files"
echo "总行数: $total_rows"

if [ -f "temp_all_sectors.txt" ]; then
    echo ""
    echo "=== 行业分布（前20名）==="
    
    # 统计并排序
    sort "temp_all_sectors.txt" | uniq -c | sort -rn > "$sector_stats_file"
    
    # 显示前20
    head -20 "$sector_stats_file"
    
    # 计算Unknown比例
    total_sectors=$(wc -l < "temp_all_sectors.txt")
    unknown_sectors=$(grep -c "^Unknown$" "temp_all_sectors.txt" 2>/dev/null || echo "0")
    
    if [ "$total_sectors" -gt 0 ]; then
        unknown_percent=$((unknown_sectors * 100 / total_sectors))
        echo ""
        echo "Unknown比例: $unknown_percent% ($unknown_sectors/$total_sectors)"
        
        if [ $unknown_percent -lt 5 ]; then
            echo "✓ 优秀！Unknown比例低于5%"
        elif [ $unknown_percent -lt 10 ]; then
            echo "✓ 良好！Unknown比例低于10%"
        elif [ $unknown_percent -lt 20 ]; then
            echo "⚠ 一般！Unknown比例10-20%，考虑补充映射"
        else
            echo "⚠ 较差！Unknown比例高于20%，需要补充映射"
        fi
    fi
    
    # 清理临时文件
    rm -f "temp_all_sectors.txt"
    
    # 生成未映射的代码报告
    echo ""
    echo "=== 未映射的Sector代码（如果存在）==="
    if [ -f "missing_codes_to_research.txt" ] && [ -s "missing_codes_to_research.txt" ]; then
        echo "未映射的代码已保存到: missing_codes_to_research.txt"
        echo "前10个未映射代码:"
        grep -v "===" missing_codes_to_research.txt | head -10
    else
        echo "没有未映射的代码，太好了！"
    fi
fi

echo ""
echo "=== 输出信息 ==="
echo "处理后的文件: $OUTPUT_DIR/"
echo "审计日志: $AUDIT_DIR/"
echo "行业分布统计: $sector_stats_file"
echo ""
echo "=== 验证示例 ==="
if [ -f "$OUTPUT_DIR/normalized_20251223.csv" ]; then
    echo "查看最新文件的示例:"
    head -3 "$OUTPUT_DIR/normalized_20251223.csv" | column -t -s,
fi
