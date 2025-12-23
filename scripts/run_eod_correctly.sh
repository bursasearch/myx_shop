#!/bin/bash
# run_eod_correctly.sh - 正确运行EOD脚本

cd /storage/emulated/0/bursasearch/myx_shop/scripts

echo "🚀 正确运行EOD脚本"
echo "时间: $(date '+%H:%M:%S')"
echo ""

# 检查可用的输入文件
echo "📁 检查可用输入文件："
find ../data -name "*.csv" -o -name "*.json" 2>/dev/null | head -10
find . -name "*.csv" -o -name "*.json" 2>/dev/null | head -10

echo ""
echo "请选择要运行的脚本："
echo "1. eod_processor.py (需要输入文件)"
echo "2. generate_json_from_eod.py"
echo "3. normalize_eod.py"
echo "4. 查看所有脚本"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "运行 eod_processor.py..."
        echo "可用输入文件："
        ls ../data/*.csv ../data/*.json 2>/dev/null | head -5
        ls *.csv *.json 2>/dev/null | head -5
        
        read -p "请输入输入文件路径: " input_file
        if [ -f "$input_file" ]; then
            echo "运行: python3 eod_processor.py \"$input_file\""
            python3 eod_processor.py "$input_file"
        else
            echo "❌ 文件不存在: $input_file"
            echo "尝试默认文件..."
            # 尝试常见文件
            for file in ../data/eod_data.csv ../data/latest.csv eod_data.csv; do
                if [ -f "$file" ]; then
                    echo "使用: $file"
                    python3 eod_processor.py "$file"
                    break
                fi
            done
        fi
        ;;
    2)
        echo "运行 generate_json_from_eod.py..."
        python3 generate_json_from_eod.py
        ;;
    3)
        echo "运行 normalize_eod.py..."
        python3 normalize_eod.py
        ;;
    4)
        echo "📋 所有可用脚本："
        ls *.py | grep -v "__pycache__"
        echo ""
        read -p "请输入脚本名: " script_name
        if [ -f "$script_name" ]; then
            # 检查是否需要参数
            echo "检查脚本参数..."
            python3 "$script_name" --help 2>/dev/null | head -10
            echo ""
            read -p "是否需要参数？(y/n): " need_args
            if [ "$need_args" = "y" ]; then
                read -p "请输入参数: " script_args
                python3 "$script_name" $script_args
            else
                python3 "$script_name"
            fi
        else
            echo "❌ 脚本不存在"
        fi
        ;;
    *)
        echo "无效选择"
        ;;
esac

echo -e "\n✅ 脚本执行完成"
