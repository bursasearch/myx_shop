#!/usr/bin/env python3
"""
======================================================================
📊 EOD CSV 自动列重排工具 (带行业代码转换)
======================================================================
功能: 自动将下载的EOD CSV文件重新排列为标准格式，并转换行业代码
使用: python reorder_eod.py [输入文件] [输出文件]
======================================================================
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
import argparse

# 目标列顺序
TARGET_COLUMNS = [
    'Code',
    'Stock', 
    'Sector',
    'Sector_Code',  # 新增：保留原始行业代码
    'Sector_Name',  # 新增：行业名称
    'Open',
    'Last',
    'Prv Close',
    'Chg%',
    'High',
    'Low',
    'Y-High',
    'Y-Low',
    'Vol',
    'DY*',
    'B%',
    'Vol MA (20)',
    'RSI (14)',
    'MACD (26, 12)',
    'EPS*',
    'P/E',
    'Status'
]

# 行业代码转换函数
def load_sector_mapping():
    """加载行业代码映射"""
    mapping_file = os.path.join(os.path.dirname(__file__), 'sector_mapping.json')
    
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("⚠️  行业映射文件不存在，使用默认映射")
        # 创建默认映射
        default_mapping = {
            "101": "Industrial & Consumer Products",
            "301": "Technology",
            "401": "Property", 
            "501": "Telecommunications & Media",
            "653": "Transportation & Logistics",
            "701": "Utilities",
            "705": "Utilities",
            "1201": "Financial Holding Firms",
            "0080": "Special Purpose Acquisition"
        }
        return default_mapping

def map_sector_code(code, sector_mapping):
    """转换行业代码为行业名称"""
    if pd.isna(code) or code in ["", "-", "N/A", "NULL"]:
        return "Unknown", ""
    
    code_str = str(code).strip()
    
    # 尝试直接匹配
    if code_str in sector_mapping:
        return sector_mapping[code_str], code_str
    
    # 尝试去除前导零匹配
    if code_str.startswith('0'):
        code_no_zero = code_str.lstrip('0')
        if code_no_zero in sector_mapping:
            return sector_mapping[code_no_zero], code_str
    
    # 尝试3位代码匹配
    if len(code_str) > 3:
        code_3digit = code_str[:3]
        if code_3digit in sector_mapping:
            return sector_mapping[code_3digit], code_str
    
    # 尝试2位代码匹配
    if len(code_str) >= 2:
        code_2digit = code_str[:2]
        # 检查是否是数字
        if code_2digit.isdigit():
            code_int = int(code_2digit)
            if 1 <= code_int <= 10:
                default_map = {
                    "1": "Industrial & Consumer Products",
                    "2": "Technology",
                    "3": "Property",
                    "4": "Telecommunications & Media", 
                    "5": "Transportation & Logistics",
                    "6": "Utilities",
                    "7": "Medical",
                    "8": "Financial",
                    "9": "Energy",
                    "10": "Consumer"
                }
                if str(code_int) in default_map:
                    return default_map[str(code_int)], code_str
    
    # 未找到匹配
    return f"Unknown ({code_str})", code_str

def process_eod_file(input_file, output_file=None, convert_sector=True):
    """处理EOD文件"""
    print("="*60)
    print(f"📁 输入文件: {input_file}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 加载行业映射
    if convert_sector:
        sector_mapping = load_sector_mapping()
        print(f"📊 加载行业映射: {len(sector_mapping)} 个代码")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(input_file)
        print(f"✅ 成功读取: {len(df)} 行 × {len(df.columns)} 列")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False
    
    # 显示原始列
    print(f"\n📋 原始列名:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    # 清理列名
    df.columns = [col.strip() for col in df.columns]
    
    # 行业代码转换
    if convert_sector and 'Sector' in df.columns:
        print(f"\n🏢 行业代码转换:")
        
        # 获取原始行业代码分布
        sector_counts = df['Sector'].value_counts()
        print(f"  发现 {len(sector_counts)} 个不同行业代码")
        
        # 转换行业代码
        sector_info = []
        for code in df['Sector'].unique():
            if pd.notna(code):
                name, _ = map_sector_code(code, sector_mapping)
                count = sector_counts.get(code, 0)
                sector_info.append((code, name, count))
        
        # 显示前10个最常见的行业
        sector_info.sort(key=lambda x: x[2], reverse=True)
        print(f"  前10个行业:")
        for code, name, count in sector_info[:10]:
            print(f"    {code}: {name} ({count} 支股票)")
        
        if len(sector_info) > 10:
            print(f"    ... 还有 {len(sector_info)-10} 个行业")
        
        # 应用转换
        df['Sector_Code'] = df['Sector']
        df['Sector_Name'] = df['Sector'].apply(lambda x: map_sector_code(x, sector_mapping)[0])
        
        # 更新Sector列为行业名称
        df['Sector'] = df['Sector_Name']
    
    # 重新排列列顺序
    print(f"\n📊 重新排列列顺序...")
    
    # 找到实际存在的列
    existing_columns = [col for col in TARGET_COLUMNS if col in df.columns]
    missing_columns = [col for col in TARGET_COLUMNS if col not in df.columns]
    
    print(f"✅ 存在的列 ({len(existing_columns)}):")
    for i, col in enumerate(existing_columns, 1):
        print(f"  {i:2d}. {col}")
    
    if missing_columns:
        print(f"⚠️  缺失的列 ({len(missing_columns)}): {missing_columns}")
        
        # 为缺失的列创建空列
        for col in missing_columns:
            if col == 'Chg%' and 'Last' in df.columns and 'Prv Close' in df.columns:
                # 计算涨跌幅
                try:
                    df['Chg%'] = ((df['Last'] - df['Prv Close']) / df['Prv Close'] * 100).round(2)
                    print(f"  📈 计算Chg%列")
                except:
                    df['Chg%'] = 0
            elif col not in df.columns:
                df[col] = ''
    
    # 保留原始数据中额外的列（添加到最后）
    extra_columns = [col for col in df.columns if col not in TARGET_COLUMNS]
    
    # 最终列顺序：目标列 + 额外列
    final_columns = [col for col in TARGET_COLUMNS if col in df.columns] + extra_columns
    df = df[final_columns]
    
    # 生成输出文件名
    if output_file is None:
        input_dir = os.path.dirname(input_file)
        input_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(input_name)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(input_dir, f"{name_without_ext}_reordered_{timestamp}.csv")
    
    # 保存文件
    try:
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n💾 保存文件: {output_file}")
        print(f"📊 最终数据: {len(df)} 行 × {len(df.columns)} 列")
        
        # 显示样本数据
        print(f"\n📄 样本数据（前3行）:")
        sample_cols = ['Code', 'Stock', 'Sector', 'Sector_Code', 'Sector_Name', 'Last', 'Chg%']
        sample_cols = [col for col in sample_cols if col in df.columns]
        
        if len(sample_cols) > 0:
            print(df.head(3)[sample_cols].to_string(index=False))
        
        # 行业统计
        if 'Sector_Name' in df.columns:
            print(f"\n🏢 行业分布统计:")
            sector_dist = df['Sector_Name'].value_counts()
            for sector, count in sector_dist.head(10).items():
                percentage = (count / len(df) * 100)
                print(f"  {sector}: {count} 支股票 ({percentage:.1f}%)")
            
            if len(sector_dist) > 10:
                print(f"  ... 还有 {len(sector_dist)-10} 个行业")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='EOD CSV文件列重排工具 (带行业代码转换)')
    parser.add_argument('input', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径（可选）')
    parser.add_argument('-a', '--auto', action='store_true', help='自动模式，使用默认输出路径')
    parser.add_argument('--no-sector', action='store_true', help='不转换行业代码')
    
    args = parser.parse_args()
    
    if args.auto:
        # 自动模式：在同目录生成重排文件
        input_dir = os.path.dirname(args.input)
        input_name = os.path.basename(args.input)
        name_without_ext = os.path.splitext(input_name)[0]
        output_file = os.path.join(input_dir, f"{name_without_ext}_reordered.csv")
        args.output = output_file
    
    success = process_eod_file(args.input, args.output, not args.no_sector)
    
    if success:
        print("\n" + "="*60)
        print("🎉 处理完成！")
        print("="*60)
    else:
        print("\n❌ 处理失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
