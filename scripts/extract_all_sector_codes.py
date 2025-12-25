#!/usr/bin/env python3
import os
import csv
import json
from collections import defaultdict

def extract_sector_codes():
    """从所有CSV文件中提取股票代码和Sector代码"""
    
    input_dir = "/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
    output_file = "all_sector_codes.json"
    
    # 存储结果
    code_to_sectors = defaultdict(set)  # 股票代码 -> Sector代码集合
    sector_stats = defaultdict(int)     # Sector代码统计
    file_sector_counts = []             # 每个文件有Sector列的行数
    
    if not os.path.exists(input_dir):
        print(f"目录不存在: {input_dir}")
        return
    
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    csv_files.sort()  # 按日期排序
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    print("最近的文件（可能有Sector列）:")
    for f in csv_files[-10:]:
        print(f"  {f}")
    
    for filename in csv_files:
        filepath = os.path.join(input_dir, filename)
        has_sector = False
        sector_count = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # 尝试检测编码和分隔符
                first_line = f.readline()
                f.seek(0)
                
                # 检查是否有Sector列
                reader = csv.reader(f)
                header = next(reader)
                
                if "Sector" in header:
                    has_sector = True
                    sector_idx = header.index("Sector")
                    
                    # 找到Code列
                    code_idx = -1
                    for i, col in enumerate(header):
                        if col.lower() in ["code", "stock code", "代码"]:
                            code_idx = i
                            break
                    
                    if code_idx != -1:
                        for row in reader:
                            if len(row) > max(code_idx, sector_idx):
                                code = row[code_idx].strip()
                                sector = row[sector_idx].strip()
                                
                                # 清理Code格式
                                if code.startswith('="') and code.endswith('"'):
                                    code = code[2:-1]
                                elif code.startswith('"') and code.endswith('"'):
                                    code = code[1:-1]
                                
                                if code and sector and sector != "-" and sector != "":
                                    code_to_sectors[code].add(sector)
                                    sector_stats[sector] += 1
                                    sector_count += 1
            
            if has_sector:
                file_sector_counts.append((filename, sector_count))
                
        except Exception as e:
            print(f"处理 {filename} 时出错: {e}")
            continue
    
    # 转换集合为列表以便JSON序列化
    code_to_sectors_serializable = {}
    for code, sectors in code_to_sectors.items():
        code_to_sectors_serializable[code] = list(sectors)
    
    # 保存结果
    result = {
        "total_files_scanned": len(csv_files),
        "files_with_sector_column": len(file_sector_counts),
        "total_unique_codes": len(code_to_sectors_serializable),
        "total_sector_mappings": sum(len(sectors) for sectors in code_to_sectors_serializable.values()),
        "sector_code_statistics": dict(sector_stats),
        "files_with_sector_details": file_sector_counts,
        "code_to_sectors": code_to_sectors_serializable
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 提取完成！结果已保存到 {output_file}")
    print(f"  扫描文件数: {len(csv_files)}")
    print(f"  有Sector列的文件: {len(file_sector_counts)}")
    print(f"  唯一股票代码数: {len(code_to_sectors_serializable)}")
    print(f"  总映射数量: {result['total_sector_mappings']}")
    
    # 显示最近文件的Sector情况
    print("\n最近文件的Sector统计:")
    for filename, count in sorted(file_sector_counts, key=lambda x: x[0])[-10:]:
        print(f"  {filename}: {count} 行有Sector")
    
    # 显示最常见的Sector代码
    print("\n最常见的Sector代码（前20个）:")
    for sector, count in sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {sector}: {count} 次")
    
    return result

if __name__ == "__main__":
    extract_sector_codes()
