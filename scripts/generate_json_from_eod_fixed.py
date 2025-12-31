#!/usr/bin/env python3
"""
从EOD CSV生成HTML所需的JSON文件 - 修复版
修复股票代码格式问题
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import glob
from datetime import datetime, timedelta
import re

def clean_stock_code(code):
    """
    清理股票代码格式
    """
    if not isinstance(code, str):
        return code
    
    # 移除开头的等号和引号
    code = re.sub(r'^[=\'"\s]+', '', code)
    # 移除结尾的引号和空格
    code = re.sub(r'[\'"\s]+$', '', code)
    
    # 移除常见的后缀
    code = re.sub(r'\s*-\s*(CW|CA|CF|CR|H|MR|WB)\s*$', '', code, flags=re.I)
    code = re.sub(r'\s*\([^)]*\)\s*$', '', code)
    
    # 统一为大写并去除空格
    code = code.strip().upper()
    
    # 特殊处理
    special_cases = {
        "0652MR": "0652",
        "HSI-CWMR": "HSICW",
        '="0652"': "0652",
        '="HSI-CW"': "HSICW",
    }
    
    return special_cases.get(code, code)

def load_eod_csv(csv_path):
    """
    加载经纪商提供的EOD CSV文件
    支持多种格式：Excel导出、CSV、TSV等
    """
    print(f"📁 加载EOD文件: {csv_path}")

    try:
        # 尝试不同的编码
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                # 读取CSV文件
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✅ 使用编码: {encoding}")
                print(f"📊 数据形状: {df.shape}")
                print(f"📋 列名: {list(df.columns)}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"❌ 编码 {encoding} 错误: {str(e)}")
                continue

        print("❌ 所有编码都失败，尝试使用错误处理...")
        df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
        return df

    except Exception as e:
        print(f"❌ 加载CSV失败: {e}")
        return None

def clean_column_names(df):
    """
    清理和标准化列名
    """
    print("\n🔧 列名清理后:")
    original_columns = list(df.columns)
    
    # 创建列名映射
    column_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # 股票代码列
        if any(keyword in col_lower for keyword in ['code', 'ticker', 'symbol']):
            column_mapping[col] = 'code'
            print(f"  ✅ 找到代码列: {col} → code")
        
        # 股票名称列
        elif any(keyword in col_lower for keyword in ['stock', 'name', 'company']):
            column_mapping[col] = 'name'
            print(f"  ✅ 找到名称列: {col} → name")
        
        # 最新价格列
        elif any(keyword in col_lower for keyword in ['last', 'price', 'close', 'last price']):
            column_mapping[col] = 'last_price'
            print(f"  ✅ 找到价格列: {col} → last_price")
        
        # 涨跌幅列
        elif any(keyword in col_lower for keyword in ['chg%', 'change%', '% change', 'change']):
            column_mapping[col] = 'change_percent'
            print(f"  ✅ 找到涨跌幅列: {col} → change_percent")
        
        # 成交量列
        elif any(keyword in col_lower for keyword in ['vol', 'volume', 'vol ma', 'vol_ma']):
            column_mapping[col] = 'volume'
            print(f"  ✅ 找到成交量列: {col} → volume")
        
        # 行业列
        elif any(keyword in col_lower for keyword in ['sector', 'industry']):
            column_mapping[col] = 'sector'
            print(f"  ✅ 找到行业列: {col} → sector")
    
    # 应用列名重命名
    df = df.rename(columns=column_mapping)
    
    # 清理股票代码列
    if 'code' in df.columns:
        df['code'] = df['code'].apply(clean_stock_code)
        print(f"  🔧 已清理股票代码列")
    
    return df

def generate_ai_picks(df, top_n=20):
    """
    生成AI选股推荐
    """
    print(f"\n🤖 生成AI选股推荐 (前{top_n}名)...")
    
    try:
        # 确保有必要的列
        required_cols = ['code', 'name', 'last_price', 'change_percent', 'sector']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"⚠️  缺少列: {missing_cols}")
            return []
        
        # 创建选股评分（示例逻辑）
        picks = []
        
        # 按涨幅排序
        df_sorted = df.sort_values('change_percent', ascending=False)
        
        # 选取前top_n只股票
        for i, (idx, row) in enumerate(df_sorted.head(top_n).iterrows(), 1):
            try:
                pick = {
                    'rank': i,
                    'code': row['code'],
                    'name': row['name'],
                    'last_price': float(row['last_price']) if pd.notna(row['last_price']) else 0,
                    'change_percent': float(row['change_percent']) if pd.notna(row['change_percent']) else 0,
                    'sector': row['sector'] if pd.notna(row['sector']) else '未知',
                    'ai_score': min(100, 80 + i),  # 示例评分
                    'potential_score': min(100, 85 + i)  # 示例潜力评分
                }
                picks.append(pick)
            except Exception as e:
                print(f"⚠️  处理第{i}行失败: {e}")
                continue
        
        print(f"✅ 成功生成 {len(picks)} 个AI选股推荐")
        return picks
    
    except Exception as e:
        print(f"❌ 生成AI选股失败: {e}")
        return []

def generate_price_data(df):
    """
    生成最新股价数据
    """
    print(f"\n📈 生成最新股价数据...")
    
    try:
        price_data = []
        
        for idx, row in df.iterrows():
            try:
                # 清理数据
                code = clean_stock_code(row.get('code', ''))
                name = str(row.get('name', '')).strip()
                
                item = {
                    'code': code,
                    'name': name,
                    'last_price': float(row['last_price']) if pd.notna(row.get('last_price')) else 0,
                    'change_percent': float(row['change_percent']) if pd.notna(row.get('change_percent')) else 0,
                    'sector': str(row.get('sector', '')).strip(),
                }
                
                # 添加其他可用字段
                for col in df.columns:
                    if col not in ['code', 'name', 'last_price', 'change_percent', 'sector']:
                        value = row[col]
                        if pd.notna(value):
                            # 尝试转换为数字
                            try:
                                item[col] = float(value)
                            except:
                                item[col] = str(value)
                
                price_data.append(item)
                
            except Exception as e:
                continue
        
        print(f"✅ 成功生成 {len(price_data)} 个股价数据")
        return price_data
    
    except Exception as e:
        print(f"❌ 生成股价数据失败: {e}")
        return []

def save_json(data, filepath, description=""):
    """
    保存数据为JSON文件
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filepath)
        if description:
            print(f"💾 {description}: {filepath} ({file_size} bytes)")
        else:
            print(f"💾 保存到: {filepath} ({file_size} bytes)")
        
        return True
    except Exception as e:
        print(f"❌ 保存失败 {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("🏦 EOD CSV 转 JSON 生成器 (修复版)")
    print("为 retail-inv.html 提供实时数据")
    print("=" * 70)
    
    if len(sys.argv) != 2:
        print("用法: python generate_json_from_eod_fixed.py <csv_file>")
        print("示例: python generate_json_from_eod_fixed.py eod_20251230.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        sys.exit(1)
    
    # 从文件名提取日期
    filename = os.path.basename(csv_path)
    date_match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', filename)
    if date_match:
        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 加载数据
    df = load_eod_csv(csv_path)
    if df is None or df.empty:
        print("❌ 无法加载数据，程序退出")
        sys.exit(1)
    
    # 清理列名和数据
    df = clean_column_names(df)
    
    # 生成AI选股
    ai_picks = generate_ai_picks(df, top_n=20)
    
    # 生成股价数据
    price_data = generate_price_data(df)
    
    # 准备输出数据
    output_dir = "."
    history_dir = "history"
    os.makedirs(history_dir, exist_ok=True)
    
    # 1. AI选股数据
    if ai_picks:
        picks_data = {
            "date": date_str,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source": filename,
            "total_picks": len(ai_picks),
            "picks": ai_picks
        }
        
        # 保存为最新文件
        save_json(picks_data, os.path.join(output_dir, "picks_latest.json"), "AI选股推荐")
        
        # 保存为历史文件
        history_date = date_str.replace('-', '')
        history_file = os.path.join(history_dir, f"picks_{history_date}.json")
        save_json(picks_data, history_file, "历史选股")
    
    # 2. 最新股价数据
    if price_data:
        price_json = {
            "date": date_str,
            "total_stocks": len(price_data),
            "stocks": price_data
        }
        save_json(price_json, os.path.join(output_dir, "latest_price.json"), "最新股价")
    
    # 3. 网页数据
    web_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_stocks": len(price_data) if price_data else 0,
        "ai_picks_count": len(ai_picks) if ai_picks else 0
    }
    save_json(web_data, os.path.join(output_dir, "data.json"), "HTML页面数据")
    
    print("\n" + "=" * 70)
    print("🎉 JSON文件生成完成！")
    print("=" * 70)
    print(f"📊 输入数据: {len(df)} 行")
    print(f"🎯 AI选股: {len(ai_picks) if ai_picks else 0} 个推荐")
    print(f"📈 股价数据: {len(price_data) if price_data else 0} 只股票")
    print("\n📁 生成的文件:")
    print(f"  • picks_latest.json     - AI选股推荐")
    print(f"  • latest_price.json     - 最新股价")
    print(f"  • history/picks_YYYYMMDD.json - 历史选股")
    print(f"  • data.json             - HTML页面数据")
    print("\n🌐 现在可以直接使用 retail-inv.html 了！")
    print("=" * 70)

if __name__ == "__main__":
    main()
