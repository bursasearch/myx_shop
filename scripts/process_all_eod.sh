#!/bin/bash
# 批量处理所有EOD CSV文件

# 使用正确的路径
INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_output"
CONFIG_FILE="./eod_config.json"
AUDIT_DIR="./audit_logs"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$AUDIT_DIR"

# 检查输入目录是否存在
if [ ! -d "$INPUT_DIR" ]; then
    echo "错误: 输入目录不存在: $INPUT_DIR"
    exit 1
fi

# 统计文件数量
file_count=$(ls "$INPUT_DIR"/*.csv 2>/dev/null | wc -l)
echo "找到 $file_count 个CSV文件"
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 处理每个CSV文件
count=0
processed=0
failed=0
for input_file in "$INPUT_DIR"/*.csv; do
    if [ -f "$input_file" ]; then
        # 获取文件名（不含路径和扩展名）
        filename=$(basename "$input_file" .csv)
        
        # 设置输出文件路径
        output_file="$OUTPUT_DIR/normalized_${filename}.csv"
        audit_file="$AUDIT_DIR/audit_${filename}.json"
        
        count=$((count + 1))
        echo "[$count/$file_count] 处理: $filename"
        
        # 运行规范化脚本
        python3 normalize_eod.py "$input_file" "$output_file" "$CONFIG_FILE" "$audit_file"
        
        if [ $? -eq 0 ]; then
            echo "  ✓ 完成: $(basename "$output_file")"
            processed=$((processed + 1))
        else
            echo "  ✗ 失败: $filename"
            failed=$((failed + 1))
        fi
    fi
done

echo ""
echo "========================================"
echo "批量处理完成！"
echo "总共: $file_count 个文件"
echo "成功: $processed 个"
echo "失败: $failed 个"
echo "输出目录: $(pwd)/$OUTPUT_DIR"
echo "审计日志: $(pwd)/$AUDIT_DIR"
echo "========================================"
