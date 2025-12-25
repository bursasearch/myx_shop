#!/data/data/com.termux/files/usr/bin/bash

# 使用方法: ./reorder_csv.sh [目录路径]
# 如果不指定路径，默认处理当前目录的所有 .csv 文件

DIR="."
if [ -n "$1" ]; then
    DIR="$1"
fi

# 指定的列顺序
DESIRED_ORDER=(
    "Code"
    "Stock"
    "Sector"
    "Open"
    "Last"
    "Prv Close"
    "Chg"
    "High"
    "Low"
    "Y-High"
    "Y-Low"
    "Vol"
    "DY*"
    "B%"
    "Vol MA (20)"
    "RSI (14)"
    "MACD (26, 12)"
    "EPS*"
    "P/E"
    "Status"
)

# 创建临时的 Python 脚本
PYTHON_SCRIPT=$(cat << 'PY'
import csv
import sys
import os
import glob

dir_path = sys.argv[1]
csv_files = glob.glob(os.path.join(dir_path, "*.csv"))

desired_order = [
    "Code",
    "Stock",
    "Sector",
    "Open",
    "Last",
    "Prv Close",
    "Chg",
    "High",
    "Low",
    "Y-High",
    "Y-Low",
    "Vol",
    "DY*",
    "B%",
    "Vol MA (20)",
    "RSI (14)",
    "MACD (26, 12)",
    "EPS*",
    "P/E",
    "Status"
]

for file_path in csv_files:
    if os.path.getsize(file_path) == 0:
        print(f"跳过空文件: {file_path}")
        continue
    
    with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            print(f"无表头: {file_path}")
            continue
        
        # 去除表头列名的首尾空格
        header = [col.strip() for col in header]
        
        # 映射列名到索引
        col_map = {name: idx for idx, name in enumerate(header)}
        
        # 找出存在的列索引，按 desired_order 顺序
        new_indices = []
        missing = []
        for col in desired_order:
            if col in col_map:
                new_indices.append(col_map[col])
            else:
                missing.append(col)
        
        if missing:
            print(f"{os.path.basename(file_path)} 缺少列: {', '.join(missing)}")
        
        # 重新排序表头
        new_header = [header[i] for i in new_indices]
        
        # 读取所有行并重新排序
        rows = [row for row in reader]
        new_rows = []
        for row in rows:
            # 确保行长度与原始表头一致
            padded_row = row + [''] * (len(header) - len(row))
            new_row = [padded_row[i] for i in new_indices]
            new_rows.append(new_row)
    
    # 输出到新文件
    output_path = file_path.replace(".csv", "_reordered.csv")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(new_header)
        writer.writerows(new_rows)
    
    print(f"处理完成: {os.path.basename(file_path)} -> {os.path.basename(output_path)}")

print("所有文件处理完毕！")
PY
)

# 执行 Python 脚本
python3 -c "$PYTHON_SCRIPT" "$DIR"
