#!/usr/bin/env python3
"""
极简版EOD处理脚本
专门处理您的CSV格式
"""
import sys
import csv
import json
import os
import re
from datetime import datetime, timezone

def main():
    print("=== 极简版EOD处理器 ===")
    
    if len(sys.argv) < 4:
        print("用法: python3 normalize_eod_simple.py 输入.csv 输出.csv 配置.json")
        print("示例: python3 normalize_eod_simple.py input.csv output.json eod_config.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    config_file = sys.argv[3]
    
    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    print(f"配置: {config_file}")
    
    # 1. 检查文件
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 - {input_file}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在 - {config_file}")
        sys.exit(1)
    
    # 2. 加载配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"错误: 无法加载配置 - {e}")
        sys.exit(1)
    
    schema = config.get("schema", [])
    aliases = config.get("map", {})
    defaults = config.get("fill", {})
    sector_lookup = config.get("sector_lookup", {})
    
    print(f"Schema: {len(schema)} 列")
    print(f"Sector映射: {len(sector_lookup)} 条")
    
    # 3. 读取CSV
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # 先读取第一行确定列顺序
            first_line = f.readline().strip()
            f.seek(0)
            
            # 检测分隔符
            if '\t' in first_line and first_line.count('\t') > first_line.count(','):
                delimiter = '\t'
                print("检测到制表符分隔")
            else:
                delimiter = ','
                print("检测到逗号分隔")
            
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
            
    except Exception as e:
        print(f"错误: 无法读取CSV - {e}")
        sys.exit(1)
    
    if len(rows) < 2:
        print("错误: CSV文件至少需要标题行和一行数据")
        sys.exit(1)
    
    print(f"读取成功: {len(rows)} 行")
    
    # 4. 处理标题行
    raw_header = rows[0]
    print(f"原始标题: {raw_header}")
    
    # 标准化标题
    header = []
    for col in raw_header:
        col = col.strip()
        # 特殊处理Chg%
        if col == "Chg%":
            col = "Chg"
        header.append(aliases.get(col, col))
    
    print(f"标准化标题: {header}")
    
    # 5. 创建输出数据
    output_rows = []
    output_rows.append(schema)  # 添加标题行
    
    stats = {
        "total": 0,
        "sector_unknown": 0,
        "sector_mapped": 0
    }
    
    for row in rows[1:]:
        if len(row) < len(header):
            # 补全缺失的列
            row = row + [''] * (len(header) - len(row))
        
        # 创建记录字典
        record = {}
        for i, col_name in enumerate(header):
            if i < len(row):
                value = row[i].strip()
            else:
                value = ""
            
            # 清理特殊值
            if value in ['', '-', '--', 'N/A']:
                value = None
            
            record[col_name] = value
        
        # 处理Code列
        code = record.get("Code", "")
        if code and code.startswith('="') and code.endswith('"'):
            code = code[2:-1]
            record["Code"] = code
        
        # 处理Sector列
        sector_code = record.get("Sector", "")
        sector_name = "Unknown"
        
        if sector_code:
            if sector_code in sector_lookup:
                sector_name = sector_lookup[sector_code]
                stats["sector_mapped"] += 1
            elif sector_code.isdigit():
                # 尝试根据首数字推断
                first_digit = sector_code[0]
                if first_digit in sector_lookup:
                    sector_name = sector_lookup[first_digit]
                    stats["sector_mapped"] += 1
                else:
                    stats["sector_unknown"] += 1
            else:
                stats["sector_unknown"] += 1
        else:
            stats["sector_unknown"] += 1
        
        record["Sector"] = sector_name
        
        # 填充默认值
        for col in schema:
            if col not in record or record[col] is None:
                record[col] = defaults.get(col, "-")
        
        # 创建输出行（按照schema顺序）
        output_row = []
        for col in schema:
            output_row.append(str(record.get(col, "-")))
        
        output_rows.append(output_row)
        stats["total"] += 1
        
        # 显示前3行示例
        if stats["total"] <= 3:
            print(f"\n示例行 {stats['total']}:")
            print(f"  Code: {record.get('Code')}, Sector: {sector_code} -> {sector_name}")
            print(f"  Chg: {record.get('Chg')}")
    
    # 6. 写入输出文件
    try:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(output_rows)
        
        print(f"\n✓ 处理完成!")
        print(f"  总行数: {stats['total']}")
        print(f"  Sector已映射: {stats['sector_mapped']}")
        print(f"  Sector未知: {stats['sector_unknown']}")
        
        if stats['total'] > 0:
            mapped_percent = (stats['sector_mapped'] / stats['total']) * 100
            print(f"  映射比例: {mapped_percent:.1f}%")
        
        print(f"  输出文件: {output_file}")
        
        # 显示Sector分布
        print("\nSector分布:")
        sectors = {}
        for row in output_rows[1:]:  # 跳过标题
            if len(row) > 2:  # 确保有Sector列
                sector = row[2]  # Sector是第3列
                sectors[sector] = sectors.get(sector, 0) + 1
        
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:10]:
            percent = (count / stats['total']) * 100
            print(f"  {sector}: {count} ({percent:.1f}%)")
        
    except Exception as e:
        print(f"错误: 无法写入输出文件 - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
