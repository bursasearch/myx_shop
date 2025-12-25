#!/bin/bash
echo "=== 修复并运行最终处理 ==="

# 修复process_all_now.sh中的错误
sed -i '100s/^/    /' process_all_now.sh  # 在第100行前添加空格
sed -i '100s/> "$temp_stats"/> "$temp_stats" 2>\/dev\/null || true/' process_all_now.sh

echo "脚本已修复"
echo ""

# 运行修复后的脚本
./process_all_now.sh

# 如果没有输出文件，手动统计
if [ ! -f "final_sector_distribution.txt" ] || [ ! -s "final_sector_distribution.txt" ]; then
    echo ""
    echo "=== 手动统计结果 ==="
    
    if [ -d "./normalized_now" ]; then
        echo "统计 ./normalized_now/ 目录下的文件..."
        
        # 合并所有Sector列
        cat ./normalized_now/*.csv 2>/dev/null | tail -n +2 | cut -d',' -f3 | sort | uniq -c | sort -rn > final_stats.txt
        
        if [ -s "final_stats.txt" ]; then
            echo "行业分布统计:"
            head -15 final_stats.txt
            
            total=$(awk '{sum+=$1} END{print sum}' final_stats.txt)
            unknown=$(grep "Unknown" final_stats.txt | awk '{print $1}' 2>/dev/null || echo "0")
            
            if [ "$total" -gt 0 ]; then
                unknown_percent=$((unknown * 100 / total))
                echo ""
                echo "总计: $total 行"
                echo "Unknown比例: $unknown_percent% ($unknown/$total)"
            fi
        fi
    fi
fi
