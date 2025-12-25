#!/bin/bash
# 批量处理所有EOD CSV文件

# 输入目录
INPUT_DIR="../stock_data/Myx_Data/EOD"
# 输出目录
OUTPUT_DIR="normalized_output"
# 配置文件
CONFIG_FILE="eod_config.json"
# 审计日志目录
AUDIT_DIR="audit_logs"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$AUDIT_DIR"

# 处理每个CSV文件
for input_file in "$INPUT_DIR"/*.csv; do
    if [ -f "$input_file" ]; then
        # 获取文件名（不含路径和扩展名）
        filename=$(basename "$input_file" .csv)
        
        # 设置输出文件路径
        output_file="$OUTPUT_DIR/normalized_${filename}.csv"
        audit_file="$AUDIT_DIR/audit_${filename}.json"
        
        echo "处理: $filename"
        
        # 运行规范化脚本
        python3 normalize_eod.py "$input_file" "$output_file" "$CONFIG_FILE" "$audit_file"
        
        if [ $? -eq 0 ]; then
            echo "✓ 完成: $output_file"
        else
            echo "✗ 失败: $filename"
        fi
    fi
done

echo "批量处理完成！"
