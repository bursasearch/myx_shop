#!/usr/bin/env python3
"""
EOD CSV专业处理器 - Python版
功能：列重新排序 + 行业代码转换
对应HTML版本的所有功能
"""

import pandas as pd
import numpy as np
import sys
import os
import json
from datetime import datetime
import argparse
import re

# ============================================================================
# 配置数据
# ============================================================================

# 标准列顺序
STANDARD_COLUMNS = [
    "Code", "Stock", "Sector", "Open", "Last", "Prv Close", "Chg", "High", "Low", 
    "Y-High", "Y-Low", "Vol", "DY*", "B%", "Vol MA (20)", "RSI (14)", "MACD (26,12)", 
    "EPS*", "P/E", "Status"
]

# 优化的列名映射（支持多种列名变体）
COLUMN_MAPPING = {
    "Code": ["Code", "股票代码", "代码", "Symbol", "Ticker", "代号", "证券代码", "股号"],
    "Stock": ["Stock", "股票", "名称", "Name", "公司名称", "股票名称", "公司", "股票名"],
    "Sector": ["Sector", "行业", "板块", "Industry", "行业分类", "所属行业", "产业", "板块分类"],
    "Open": ["Open", "开盘价", "开盘", "Opening Price", "开市价", "今开", "开盘价格"],
    "Last": ["Last", "最新价", "现价", "当前价", "收盘价", "最后价", "成交价", "当前价格"],
    "Prv Close": ["Prv Close", "前收盘", "昨日收盘", "Previous Close", "前收", "昨收", "前一日收盘", "昨日收市", "Prev Close"],
    "Chg": ["Chg", "涨跌", "变化", "Change", "涨跌幅", "变动", "涨幅", "变化率", "涨跌%", "Chg%", "Change%"],
    "High": ["High", "最高价", "最高", "最高价", "日内最高", "当日最高"],
    "Low": ["Low", "最低价", "最低", "最低价", "日内最低", "当日最低"],
    "Y-High": ["Y-High", "年最高", "52周最高", "Year High", "52周高", "年度最高", "年内最高", "Year-High"],
    "Y-Low": ["Y-Low", "年最低", "52周最低", "Year Low", "52周低", "年度最低", "年内最低", "Year-Low"],
    "Vol": ["Vol", "成交量", "交易量", "Volume", "成交额", "量", "成交股数", "交易股数"],
    "DY*": ["DY*", "股息率", "股息收益率", "Dividend Yield", "股息", "分红率", "股息%", "Dividend"],
    "B%": ["B%", "贝塔系数", "Beta", "波动率", "风险系数", "β", "Beta系数"],
    "Vol MA (20)": ["Vol MA (20)", "成交量均线20", "20日成交量均线", "Vol MA 20", "Volume MA 20", "20日均量", "成交量20日均线", "Vol MA(20)"],
    "RSI (14)": ["RSI (14)", "RSI", "相对强弱指数", "RSI 14", "相对强弱指标", "RSI指标"],
    "MACD (26,12)": ["MACD (26,12)", "MACD", "指数平滑异同移动平均线", "MACD指标", 
                    "MACD(26,12)", "MACD (26, 12)", "MACD(26, 12)", "MACD 26 12", 
                    "MACD(26,12,9)", "MACD (26,12,9)", "MACD 26-12"],
    "EPS*": ["EPS*", "每股收益", "EPS", "每股盈利", "每股盈余", "Earnings Per Share", "每股收益EPS"],
    "P/E": ["P/E", "市盈率", "PE", "股价收益比", "本益比", "市盈率(PE)", "PE Ratio", "P/E Ratio"],
    "Status": ["Status", "状态", "交易状态", "上市状态", "股票状态", "上市情况", "交易情况"]
}

# 行业映射数据
SECTOR_MAP = {
    "101": "Industrial & Consumer Products",
    "102": "Industrial & Consumer Products", 
    "103": "Industrial & Consumer Products",
    "105": "Industrial & Consumer Products",
    "110": "Industrial & Consumer Products",
    "120": "Industrial & Consumer Products",
    "125": "Industrial & Consumer Products",
    "150": "Industrial & Consumer Products",
    "155": "Industrial & Consumer Products",
    "161": "Industrial & Consumer Products",
    "162": "Industrial & Consumer Products",
    "163": "Industrial & Consumer Products",
    "164": "Industrial & Consumer Products",
    "165": "Industrial & Consumer Products",
    "166": "Industrial & Consumer Products",
    "301": "Technology",
    "302": "Technology",
    "303": "Technology",
    "305": "Technology",
    "310": "Technology",
    "320": "Technology",
    "325": "Technology",
    "358": "Technology",
    "361": "Technology",
    "362": "Technology",
    "363": "Technology",
    "364": "Technology",
    "365": "Technology",
    "401": "Property",
    "402": "Property",
    "403": "Property",
    "405": "Property",
    "410": "Property",
    "420": "Property",
    "425": "Property",
    "461": "Property",
    "462": "Property",
    "463": "Property",
    "464": "Property",
    "465": "Property",
    "501": "Telecommunications & Media",
    "502": "Telecommunications & Media",
    "520": "Telecommunications & Media",
    "560": "Telecommunications & Media",
    "653": "Transportation & Logistics",
    "654": "Transportation & Logistics",
    "656": "Transportation & Logistics",
    "657": "Transportation & Logistics",
    "701": "Utilities",
    "702": "Utilities",
    "703": "Utilities",
    "705": "Utilities",
    "710": "Utilities",
    "725": "Utilities",
    "762": "Utilities",
    "0162": "Medical Devices & Supplies",
    "0405": "Software & IT Services",
    "1701": "Industrial Holding Firms",
    "1702": "Industrial & Consumer Products",
    "1703": "Industrial Support Services",
    "1704": "Building Materials",
    "1705": "Construction & Infrastructure",
    "1706": "Transportation & Logistics",
    "1801": "Consumer Product Holding Firms",
    "1802": "Food, Beverage & Tobacco",
    "1803": "Retail & Distribution",
    "1804": "Hotel, Resort & Recreational Services",
    "1805": "Media & Entertainment",
    "1806": "Other Consumer Services",
    "1807": "Health Care Equipment & Services",
    "1808": "Pharmaceuticals & Biotechnology",
    "1809": "Technology",
    "1810": "Telecommunications & Media",
    "0200": "Plantation",
    "0501": "Property Holding Firms",
    "0502": "Property Development",
    "0503": "Real Estate Investment Trusts (REITs)",
    "0504": "Other Property-related Services",
    "1201": "Financial Holding Firms",
    "1202": "Commercial Banks",
    "1203": "Insurance",
    "1204": "Investment Banks",
    "1205": "Other Finance",
    "0301": "Energy Holding Firms",
    "0302": "Energy-related Equipment & Services",
    "0303": "Oil & Gas",
    "0401": "Utilities Holding Firms",
    "0402": "Gas, Water & Multi-utilities",
    "0403": "Electricity",
    "0080": "Special Purpose Acquisition",
    
    # 默认映射（数字代码转行业）
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

# ============================================================================
# 核心功能函数
# ============================================================================

def check_column_match(actual_col, standard_col):
    """
    检查实际列名是否匹配标准列名
    返回匹配分数（0-10）
    """
    if not actual_col or not standard_col:
        return 0
    
    # 清理列名
    clean_actual = str(actual_col).strip().replace('\ufeff', '').lower()
    clean_standard = str(standard_col).strip().lower()
    
    # 1. 完全匹配（10分）
    if clean_actual == clean_standard:
        return 10
    
    # 2. 检查列名映射（8分）
    if standard_col in COLUMN_MAPPING:
        for variant in COLUMN_MAPPING[standard_col]:
            if clean_actual == variant.lower():
                return 8
            if clean_actual in variant.lower() or variant.lower() in clean_actual:
                return 7
    
    # 3. 处理中文列名（7分）
    chinese_mapping = {
        "Code": ["代码", "代号", "股号"],
        "Stock": ["股票", "名称"],
        "Sector": ["行业"],
        "Open": ["开盘价", "开盘"],
        "Last": ["最新价", "收盘价"],
        "Prv Close": ["前收盘", "昨收"],
        "Chg": ["涨跌", "涨跌幅", "变化"],
        "High": ["最高价", "最高"],
        "Low": ["最低价", "最低"],
        "Y-High": ["年最高", "52周最高"],
        "Y-Low": ["年最低", "52周最低"],
        "Vol": ["成交量", "交易量"],
        "DY*": ["股息率", "股息收益率"],
        "B%": ["贝塔系数", "Beta"],
        "Vol MA (20)": ["成交量均线20", "20日成交量均线"],
        "RSI (14)": ["RSI", "相对强弱指数"],
        "MACD (26,12)": ["MACD", "指数平滑异同移动平均线"],
        "EPS*": ["每股收益", "EPS"],
        "P/E": ["市盈率", "PE"],
        "Status": ["状态", "交易状态"]
    }
    
    if standard_col in chinese_mapping:
        for chinese in chinese_mapping[standard_col]:
            if chinese in actual_col or actual_col in chinese:
                return 7
    
    # 4. 关键词匹配（6分）
    standard_words = re.findall(r'[a-zA-Z0-9]+', clean_standard)
    actual_words = re.findall(r'[a-zA-Z0-9]+', clean_actual)
    
    for word in standard_words:
        if len(word) > 2 and word in clean_actual:
            return 6
    
    # 5. 部分匹配（4分）
    for word in standard_words:
        if len(word) > 3:
            for actual_word in actual_words:
                if len(actual_word) > 3:
                    if word in actual_word or actual_word in word:
                        return 4
    
    # 6. 完全无匹配（0分）
    return 0

def auto_align_columns(df_columns):
    """
    自动对齐列到标准顺序
    返回：(target_order, mapping_info, match_score)
    """
    target_order = []
    used_columns = []
    mapping_info = []
    total_score = 0
    
    print("🔍 自动检测列匹配...")
    
    # 为每个标准列寻找最佳匹配
    for std_col in STANDARD_COLUMNS:
        best_match = None
        best_score = 0
        
        for actual_col in df_columns:
            if actual_col in used_columns:
                continue
            
            score = check_column_match(actual_col, std_col)
            
            if score > best_score:
                best_score = score
                best_match = actual_col
        
        # 如果找到匹配，添加到目标顺序
        if best_match and best_score >= 4:
            target_order.append(best_match)
            used_columns.append(best_match)
            mapping_info.append({
                "standard": std_col,
                "actual": best_match,
                "score": best_score,
                "status": "✓ 匹配" if best_score >= 6 else "⚠ 部分匹配"
            })
            total_score += best_score
            print(f"  {std_col:15} -> {best_match:20} ({best_score}/10)")
        else:
            # 如果没有找到匹配，添加标准列名（留空）
            target_order.append(std_col)
            mapping_info.append({
                "standard": std_col,
                "actual": None,
                "score": 0,
                "status": "✗ 未匹配"
            })
            print(f"  {std_col:15} -> {'[未匹配]':20} (0/10)")
    
    # 添加剩余的列
    for actual_col in df_columns:
        if actual_col not in used_columns:
            target_order.append(actual_col)
            mapping_info.append({
                "standard": "(额外)",
                "actual": actual_col,
                "score": 0,
                "status": "额外列"
            })
    
    # 计算匹配率
    matched_count = len([m for m in mapping_info if m['score'] >= 4])
    match_rate = (matched_count / len(STANDARD_COLUMNS)) * 100
    
    return target_order, mapping_info, match_rate

def apply_sector_mapping(df):
    """
    应用行业代码映射
    """
    print("🏭 应用行业代码映射...")
    
    # 查找Sector列
    sector_col = None
    for col in df.columns:
        if check_column_match(col, "Sector") >= 4:
            sector_col = col
            break
    
    if not sector_col:
        print("⚠  未找到Sector列，跳过行业映射")
        return df
    
    # 应用映射
    def map_sector(code):
        if pd.isna(code):
            return "Unknown"
        
        code_str = str(code).strip()
        
        # 直接匹配
        if code_str in SECTOR_MAP:
            return SECTOR_MAP[code_str]
        
        # 默认映射（按第一个数字）
        if code_str and code_str[0].isdigit():
            first_digit = code_str[0]
            if first_digit in SECTOR_MAP:
                return SECTOR_MAP[first_digit]
        
        # 范围匹配（101-166等）
        if code_str.isdigit():
            code_int = int(code_str)
            for key, value in SECTOR_MAP.items():
                if '-' in key:
                    start, end = map(int, key.split('-'))
                    if start <= code_int <= end:
                        return value
        
        return f"Unknown ({code_str})"
    
    df[sector_col] = df[sector_col].apply(map_sector)
    
    # 统计行业分布
    sector_counts = df[sector_col].value_counts()
    print("📊 行业分布统计:")
    for sector, count in sector_counts.head(10).items():
        percentage = (count / len(df)) * 100
        print(f"  {sector:40} {count:5} 行 ({percentage:.1f}%)")
    
    return df

def reorder_dataframe(df, target_order):
    """
    按照目标顺序重新排列DataFrame
    """
    print("🔄 重新排列数据列...")
    
    # 创建列映射
    column_mapping = {}
    
    for std_col in STANDARD_COLUMNS:
        found_col = None
        for target_col in target_order:
            if target_col in df.columns and check_column_match(target_col, std_col) >= 4:
                found_col = target_col
                break
        
        column_mapping[std_col] = found_col
    
    # 创建新的DataFrame
    new_data = {}
    
    for std_col, actual_col in column_mapping.items():
        if actual_col and actual_col in df.columns:
            new_data[std_col] = df[actual_col]
            print(f"  {std_col:15} ← {actual_col:20}")
        else:
            new_data[std_col] = pd.Series([""] * len(df))
            print(f"  {std_col:15} ← {'[空]':20}")
    
    # 添加额外的列
    for col in df.columns:
        if col not in [v for v in column_mapping.values() if v]:
            new_data[col] = df[col]
            print(f"  {col:15} ← {col:20} (额外)")
    
    result_df = pd.DataFrame(new_data)
    
    # 确保标准列顺序
    final_columns = STANDARD_COLUMNS.copy()
    for col in df.columns:
        if col not in final_columns and col not in [v for v in column_mapping.values() if v]:
            final_columns.append(col)
    
    result_df = result_df[final_columns]
    
    return result_df

def print_preview(df, title="数据预览", num_rows=10):
    """
    打印数据预览
    """
    print(f"\n📋 {title} (前{num_rows}行):")
    print("=" * 100)
    
    # 打印列名
    col_names = list(df.columns)
    col_display = [name[:15].ljust(15) for name in col_names[:8]]  # 只显示前8列
    print(" | ".join(col_display))
    print("-" * 100)
    
    # 打印数据行
    for i in range(min(num_rows, len(df))):
        row = df.iloc[i]
        row_display = []
        for col in col_names[:8]:
            value = str(row[col]) if not pd.isna(row[col]) else ""
            row_display.append(value[:15].ljust(15))
        print(" | ".join(row_display))
    
    print("=" * 100)
    print(f"总行数: {len(df)} | 总列数: {len(df.columns)}")
    
    # 显示前几列的统计信息
    print("\n📊 数据统计:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        for col in numeric_cols[:5]:  # 只显示前5个数值列
            col_data = df[col].dropna()
            if len(col_data) > 0:
                print(f"  {col:15}: 平均={col_data.mean():.2f} 最小={col_data.min():.2f} 最大={col_data.max():.2f}")

def save_results(df, input_path, output_dir=None):
    """
    保存处理结果
    """
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(input_name)[0]
    
    csv_output = os.path.join(output_dir, f"{name_without_ext}_processed_{timestamp}.csv")
    json_output = os.path.join(output_dir, f"{name_without_ext}_processed_{timestamp}.json")
    
    # 保存CSV
    df.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"💾 CSV保存到: {csv_output}")
    
    # 保存JSON（可选）
    try:
        json_data = df.to_dict(orient='records')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON保存到: {json_output}")
    except Exception as e:
        print(f"⚠  无法保存JSON: {e}")
    
    return csv_output, json_output

def process_eod_csv(input_path, output_dir=None, interactive=False):
    """
    主处理函数
    """
    print("=" * 70)
    print("🏦 EOD CSV专业处理器 - Python版")
    print("=" * 70)
    
    # 1. 读取CSV文件
    print(f"\n📁 读取文件: {input_path}")
    try:
        # 尝试不同编码
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_path, encoding=encoding)
                print(f"✅ 使用编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("无法读取CSV文件，尝试了多种编码")
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None
    
    print(f"📊 读取成功: {len(df)} 行 × {len(df.columns)} 列")
    print("原始列名:", list(df.columns))
    
    # 2. 预览原始数据
    print_preview(df, "原始数据")
    
    # 3. 自动对齐列
    target_order, mapping_info, match_rate = auto_align_columns(df.columns)
    
    print(f"\n📈 列匹配率: {match_rate:.1f}%")
    if match_rate < 70:
        print("⚠  警告: 匹配率较低，可能需要手动调整")
    
    if interactive:
        print("\n🔧 手动调整选项:")
        print("  1. 显示详细匹配信息")
        print("  2. 手动指定列映射")
        print("  3. 继续处理")
        
        choice = input("请选择 (1-3, 默认3): ").strip()
        if choice == "1":
            print("\n📋 详细匹配信息:")
            for info in mapping_info:
                if info['standard'] != "(额外)":
                    status_icon = "✓" if info['score'] >= 6 else "⚠" if info['score'] >= 4 else "✗"
                    print(f"  {status_icon} {info['standard']:15} -> {info['actual'] or '[未匹配]':20} ({info['status']})")
    
    # 4. 应用行业映射
    df = apply_sector_mapping(df)
    
    # 5. 重新排列列
    result_df = reorder_dataframe(df, target_order)
    
    # 6. 预览处理后的数据
    print_preview(result_df, "处理后的数据")
    
    # 7. 保存结果
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    csv_output, json_output = save_results(result_df, input_path, output_dir)
    
    # 8. 完成
    print("\n" + "=" * 70)
    print("🎉 处理完成！")
    print("=" * 70)
    print(f"📁 输入文件: {input_path}")
    print(f"📊 处理行数: {len(df)}")
    print(f"📈 列匹配率: {match_rate:.1f}%")
    print(f"💾 输出文件: {csv_output}")
    if os.path.exists(json_output):
        print(f"📄 JSON文件: {json_output}")
    print("=" * 70)
    
    return result_df

# ============================================================================
# 命令行接口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='EOD CSV专业处理器 - 列重新排序 + 行业代码转换')
    parser.add_argument('input', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出目录（默认为输入文件所在目录）')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    parser.add_argument('-b', '--batch', help='批量处理目录下的所有CSV文件')
    
    args = parser.parse_args()
    
    # 批量处理模式
    if args.batch:
        if not os.path.isdir(args.batch):
            print(f"❌ 目录不存在: {args.batch}")
            return
        
        csv_files = [f for f in os.listdir(args.batch) if f.lower().endswith('.csv')]
        
        if not csv_files:
            print(f"❌ 在目录中未找到CSV文件: {args.batch}")
            return
        
        print(f"🔍 找到 {len(csv_files)} 个CSV文件")
        
        for i, csv_file in enumerate(csv_files, 1):
            input_path = os.path.join(args.batch, csv_file)
            print(f"\n📁 处理文件 {i}/{len(csv_files)}: {csv_file}")
            
            try:
                process_eod_csv(input_path, args.output, args.interactive)
            except Exception as e:
                print(f"❌ 处理失败: {e}")
        
        print("\n✅ 批量处理完成！")
    
    # 单文件处理模式
    else:
        if not os.path.exists(args.input):
            print(f"❌ 文件不存在: {args.input}")
            return
        
        process_eod_csv(args.input, args.output, args.interactive)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
