#!/bin/bash

# 改进的日期提取函数
extract_date_from_filename() {
    local filename="$1"
    
    # 移除扩展名
    filename=$(basename "$filename" .csv)
    
    # 尝试不同的模式
    # 模式1: 25251230 -> 20251230 (前两位25转为2025)
    if [[ "$filename" =~ ^25([0-9]{6})$ ]]; then
        echo "2025${BASH_REMATCH[1]}"
        return 0
    fi
    
    # 模式2: 直接是8位数字
    if [[ "$filename" =~ ^[0-9]{8}$ ]]; then
        # 检查是否是合理的日期
        year="${filename:0:4}"
        month="${filename:4:2}"
        day="${filename:6:2}"
        
        if [[ "$month" =~ ^(0[1-9]|1[0-2])$ ]] && [[ "$day" =~ ^(0[1-9]|[12][0-9]|3[01])$ ]]; then
            echo "$filename"
            return 0
        fi
    fi
    
    # 模式3: 包含日期的其他格式
    if [[ "$filename" =~ [^0-9]([0-9]{4})([0-9]{2})([0-9]{2})[^0-9] ]]; then
        echo "${BASH_REMATCH[1]}${BASH_REMATCH[2]}${BASH_REMATCH[3]}"
        return 0
    fi
    
    # 默认使用今天
    date '+%Y%m%d'
}

# 测试
echo "测试日期提取:"
extract_date_from_filename "25251230.csv"
