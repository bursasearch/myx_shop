#!/usr/bin/env python3
import sys
import csv

def check_format(filepath):
    print(f"检查文件: {filepath}")
    print("="*50)
    
    try:
        # 尝试逗号分隔
        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.read(4096)
            f.seek(0)
            
            # 检查分隔符
            comma_count = sample.count(',')
            tab_count = sample.count('\t')
            print(f"逗号数量: {comma_count}")
            print(f"制表符数量: {tab_count}")
            
            if tab_count > comma_count:
                delimiter = '\t'
                print("推测为制表符分隔文件")
            else:
                delimiter = ','
                print("推测为逗号分隔文件")
            
            # 读取文件
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
            
            if not rows:
                print("空文件")
                return
            
            print(f"总行数: {len(rows)}")
            print(f"列数: {len(rows[0])}")
            print("")
            
            print("=== 列名（原始）===")
            for i, col in enumerate(rows[0], 1):
                print(f"{i:2}. '{col}'")
            
            print("")
            print("=== 第一行数据示例 ===")
            if len(rows) > 1:
                for i, (col, val) in enumerate(zip(rows[0], rows[1]), 1):
                    print(f"{i:2}. {col}: '{val}'")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 check_csv_format.py <csv文件路径>")
        sys.exit(1)
    
    check_format(sys.argv[1])
