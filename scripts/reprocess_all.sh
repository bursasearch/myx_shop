#!/bin/bash
# 重新处理所有EOD CSV文件

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_output_v2"
CONFIG_FILE="./eod_config.json"
AUDIT_DIR="./audit_logs_v2"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$AUDIT_DIR"

# 检查输入目录
if [ ! -d "$INPUT_DIR" ]; then
    echo "错误: 输入目录不存在: $INPUT_DIR"
    exit 1
fi

# 统计文件
file_count=$(ls "$INPUT_DIR"/*.csv 2>/dev/null | wc -l)
echo "找到 $file_count 个CSV文件"
echo "使用新的行业映射配置..."

# 处理文件
count=0
processed=0
failed=0
for input_file in "$INPUT_DIR"/*.csv; do
    if [ -f "$input_file" ]; then
        filename=$(basename "$input_file" .csv)
        output_file="$OUTPUT_DIR/normalized_${filename}.csv"
        audit_file="$AUDIT_DIR/audit_${filename}.json"
        
        count=$((count + 1))
        echo "[$count/$file_count] 处理: $filename"
        
        python3 normalize_eod.py "$input_file" "$output_file" "$CONFIG_FILE" "$audit_file"
        
        if [ $? -eq 0 ]; then
            processed=$((processed + 1))
            # 检查处理结果
            if [ -f "$output_file" ]; then
                # 统计Sector分布
                sectors=$(tail -n +2 "$output_file" | cut -d',' -f3 | sort | uniq -c | sort -rn)
                echo "  ✓ 完成: $(wc -l < "$output_file") 行"
                echo "  行业分布:"
                echo "$sectors" | head -5 | while read line; do
                    echo "    $line"
                done
            fi
        else
            failed=$((failed + 1))
            echo "  ✗ 失败: $filename"
        fi
    fi
done

echo ""
echo "========================================"
echo "重新处理完成！"
echo "总共: $file_count 个文件"
echo "成功: $processed 个"
echo "失败: $failed 个"
echo "输出目录: $OUTPUT_DIR"
echo "审计日志: $AUDIT_DIR"
echo "========================================"

# 生成行业统计报告
echo ""
echo "=== 行业统计报告 ==="
cat "$OUTPUT_DIR"/*.csv 2>/dev/null | tail -n +2 | cut -d',' -f3 | sort | uniq -c | sort -rn > sector_distribution.txt
echo "行业分布已保存到: sector_distribution.txt"
cat sector_distribution.txt
