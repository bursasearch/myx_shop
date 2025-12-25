#!/bin/bash
echo "=== 修复版批量处理 ==="
echo "专门处理马来西亚EOD数据"
echo ""

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
OUTPUT_DIR="./normalized_complete"
CONFIG_FILE="./eod_config.json"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 显示信息
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "配置文件: $CONFIG_FILE"

# 验证配置文件
echo -n "验证配置文件... "
python3 -c "
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    print('✓ 有效')
    print(f'Schema列数: {len(config.get(\"schema\", []))}')
    print(f'Sector映射数: {len(config.get(\"sector_lookup\", {}))}')
except Exception as e:
    print(f'✗ 无效: {e}')
    exit(1)
"

# 获取文件列表
echo ""
echo "查找CSV文件..."
files=($(find "$INPUT_DIR" -name "*.csv" -type f | sort))
total_files=${#files[@]}

if [ $total_files -eq 0 ]; then
    echo "错误: 没有找到CSV文件"
    exit 1
fi

echo "找到 $total_files 个文件"
echo ""

# 初始化统计
success=0
failed=0
total_rows=0
processed_files=0

# 处理每个文件
for input_file in "${files[@]}"; do
    filename=$(basename "$input_file" .csv)
    output_file="$OUTPUT_DIR/normalized_$filename.csv"
    
    processed_files=$((processed_files + 1))
    echo -n "[$processed_files/$total_files] $filename: "
    
    # 运行处理脚本
    python3 normalize_eod_simple.py "$input_file" "$output_file" "$CONFIG_FILE" > /tmp/process_$filename.log 2>&1
    
    # 检查结果
    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        rows=$(tail -n +2 "$output_file" | wc -l)
        total_rows=$((total_rows + rows))
        
        # 检查文件是否非空
        if [ $rows -gt 0 ]; then
            # 统计Unknown Sector
            unknown=$(grep -c ",Unknown," "$output_file" 2>/dev/null || echo "0")
            if [ $rows -gt 0 ]; then
                unknown_percent=$((unknown * 100 / rows))
                echo "✓ $rows 行, Unknown: $unknown_percent%"
            else
                echo "✓ $rows 行"
            fi
            
            success=$((success + 1))
            
            # 收集Sector统计
            tail -n +2 "$output_file" | cut -d',' -f3 >> "/tmp/all_sectors_temp.txt"
        else
            echo "✗ 输出文件为空"
            failed=$((failed + 1))
            rm -f "$output_file"  # 删除空文件
        fi
    else
        echo "✗ 处理失败"
        failed=$((failed + 1))
        
        # 显示错误信息
        if [ -f "/tmp/process_$filename.log" ]; then
            error_msg=$(tail -3 "/tmp/process_$filename.log" | grep -i "error\|fail\|异常")
            if [ -n "$error_msg" ]; then
                echo "  错误: $error_msg"
            fi
        fi
    fi
done

echo ""
echo "=== 处理统计 ==="
echo "总文件数: $total_files"
echo "成功处理: $success"
echo "失败: $failed"
echo "总行数: $total_rows"

# 生成Sector统计报告
if [ -f "/tmp/all_sectors_temp.txt" ] && [ -s "/tmp/all_sectors_temp.txt" ]; then
    echo ""
    echo "=== 总体行业分布 ==="
    
    sector_stats_file="sector_distribution_complete.txt"
    sort "/tmp/all_sectors_temp.txt" | uniq -c | sort -rn > "$sector_stats_file"
    
    echo "前15名行业:"
    head -15 "$sector_stats_file"
    
    # 计算Unknown比例
    total_sectors=$(wc -l < "/tmp/all_sectors_temp.txt")
    unknown_sectors=$(grep -c "^Unknown$" "/tmp/all_sectors_temp.txt" 2>/dev/null || echo "0")
    
    if [ $total_sectors -gt 0 ]; then
        unknown_percent=$((unknown_sectors * 100 / total_sectors))
        echo ""
        echo "Unknown比例: $unknown_percent% ($unknown_sectors/$total_sectors)"
        
        if [ $unknown_percent -lt 5 ]; then
            echo "✓ 优秀！超过95%的Sector已正确映射"
        elif [ $unknown_percent -lt 10 ]; then
            echo "✓ 良好！超过90%的Sector已正确映射"
        elif [ $unknown_percent -lt 20 ]; then
            echo "✓ 一般！超过80%的Sector已正确映射"
        else
            echo "⚠ 需要改进！Unknown比例较高"
        fi
    fi
    
    rm -f "/tmp/all_sectors_temp.txt"
    
    echo ""
    echo "完整行业分布已保存到: $sector_stats_file"
fi

# 显示示例
echo ""
echo "=== 处理结果示例 ==="
if [ $success -gt 0 ]; then
    # 找到最新的文件
    latest_file=$(ls -t "$OUTPUT_DIR"/normalized_*.csv 2>/dev/null | head -1)
    
    if [ -f "$latest_file" ]; then
        latest_name=$(basename "$latest_file")
        echo "最新文件: $latest_name"
        echo ""
        
        echo "标题行:"
        head -1 "$latest_file" | sed 's/,/ | /g'
        echo ""
        
        echo "前3行数据:"
        head -4 "$latest_file" | tail -3 | while read line; do
            echo "$line" | sed 's/,/ | /g'
        done
        
        echo ""
        echo "Sector列示例:"
        tail -n +2 "$latest_file" | cut -d',' -f3 | sort | uniq | head -5 | while read sector; do
            count=$(grep -c ",$sector," "$latest_file")
            echo "  $sector: $count 行"
        done
    fi
fi

echo ""
echo "=== 输出信息 ==="
echo "处理后的文件目录: $OUTPUT_DIR/"
echo "行业分布文件: sector_distribution_complete.txt"
echo ""
echo "=== 验证命令 ==="
echo "查看处理后的文件:"
echo "  column -t -s, $OUTPUT_DIR/normalized_20251223.csv | head -10"
echo ""
echo "统计所有文件的Sector分布:"
echo "  cat $OUTPUT_DIR/*.csv | tail -n +2 | cut -d',' -f3 | sort | uniq -c | sort -rn"
echo ""
echo "查看处理详情:"
echo "  python3 normalize_eod_simple.py \"$INPUT_DIR/20251223.csv\" test.csv eod_config.json"
