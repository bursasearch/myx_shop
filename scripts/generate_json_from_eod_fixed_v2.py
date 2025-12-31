#!/usr/bin/env python3
"""
从EOD CSV生成HTML所需的JSON文件 - 修复版 v2
修复: 
1. 股票代码格式问题
2. 列名冲突问题
3. 数据生成逻辑错误
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import re
from datetime import datetime

def clean_stock_code(code):
    """
    清理股票代码格式 - 修复版
    """
    if not isinstance(code, str):
        return str(code) if pd.notna(code) else ""
    
    # 移除开头的等号、引号和空格
    code = re.sub(r'^[=\'"\s]+', '', code)
    # 移除结尾的引号和空格
    code = re.sub(r'[\'"\s]+$', '', code)
    
    # 清理常见的Excel导出格式
    if code.startswith('="') and code.endswith('"'):
        code = code[2:-1]
    
    # 移除认股权证后缀 (CW, CA, CF等)
    code = re.sub(r'\s*[-_]?\s*(CW|CA|CF|CR|H|MR|WB|PA)\s*$', '', code, flags=re.I)
    
    # 移除括号内容
    code = re.sub(r'\s*\([^)]*\)\s*$', '', code)
    
    # 统一为大写并去除空格
    code = code.strip().upper()
    
    # 如果是纯数字，保持4位格式
    if code.isdigit():
        code = code.zfill(4)
    
    return code

def load_eod_csv(csv_path):
    """
    加载EOD CSV文件
    """
    print(f"📁 加载EOD文件: {csv_path}")

    try:
        # 尝试不同编码
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                # 尝试读取CSV
                df = pd.read_csv(csv_path, encoding=encoding, thousands=',')
                print(f"✅ 使用编码: {encoding}")
                print(f"📊 数据形状: {df.shape}")
                print(f"📋 原始列名: {list(df.columns)}")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        
        # 如果所有编码都失败，尝试使用错误处理
        print("⚠️  尝试使用错误处理模式...")
        df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip', thousands=',')
        return df
        
    except Exception as e:
        print(f"❌ 加载CSV失败: {e}")
        return None

def standardize_columns(df):
    """
    标准化列名 - 修复列名冲突问题
    """
    print("\n🔧 标准化列名...")
    
    # 创建列名映射
    column_mapping = {}
    
    for col in df.columns:
        col_str = str(col).strip()
        col_lower = col_str.lower()
        
        # 先检查是否有精确匹配
        if 'code' in col_lower and 'change' not in col_lower:
            column_mapping[col] = 'code'
            print(f"  📍 代码列: {col} → code")
            
        elif 'stock' in col_lower or ('name' in col_lower and 'change' not in col_lower):
            column_mapping[col] = 'name'
            print(f"  📍 名称列: {col} → name")
            
        elif 'last' in col_lower and 'close' not in col_lower:
            column_mapping[col] = 'last_price'
            print(f"  📍 最新价列: {col} → last_price")
            
        elif 'chg%' in col_lower or 'change%' in col_lower:
            column_mapping[col] = 'change_percent'
            print(f"  📍 涨跌幅列: {col} → change_percent")
            
        elif 'sector' in col_lower:
            column_mapping[col] = 'sector'
            print(f"  📍 行业列: {col} → sector")
            
        elif 'vol' in col_lower and 'ma' in col_lower:
            column_mapping[col] = 'volume_ma'
            print(f"  📍 成交量均线列: {col} → volume_ma")
            
        elif 'vol' in col_lower:
            column_mapping[col] = 'volume'
            print(f"  📍 成交量列: {col} → volume")
    
    # 应用重命名
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # 清理股票代码列
    if 'code' in df.columns:
        df['code'] = df['code'].apply(clean_stock_code)
        print(f"  🔧 已清理股票代码列")
    
    print(f"  📋 最终列名: {list(df.columns)}")
    
    return df

def generate_ai_picks_simple(df, top_n=20):
    """
    简单AI选股生成 - 修复逻辑错误
    """
    print(f"\n🤖 生成AI选股推荐 (前{top_n}名)...")
    
    try:
        # 确保有必要的列
        if 'code' not in df.columns or 'name' not in df.columns:
            print("❌ 缺少必要列: code 或 name")
            return []
        
        # 如果有涨跌幅，按涨跌幅排序
        if 'change_percent' in df.columns:
            # 转换为数值
            df['change_percent_num'] = pd.to_numeric(df['change_percent'], errors='coerce')
            # 按涨跌幅降序排序
            df_sorted = df.sort_values('change_percent_num', ascending=False)
        else:
            df_sorted = df
        
        # 生成选股列表
        picks = []
        count = 0
        
        for idx, row in df_sorted.iterrows():
            if count >= top_n:
                break
            
            try:
                # 获取基本数据
                code = row.get('code', '')
                name = row.get('name', '')
                
                if not code or not name:
                    continue
                
                # 构建选股对象
                pick = {
                    'rank': count + 1,
                    'code': code,
                    'name': str(name).strip(),
                    'ai_score': min(100, 80 + count),
                    'potential_score': min(100, 85 + count)
                }
                
                # 添加价格信息
                if 'last_price' in df.columns and pd.notna(row.get('last_price')):
                    try:
                        pick['last_price'] = float(row['last_price'])
                    except:
                        pick['last_price'] = 0
                
                # 添加涨跌幅
                if 'change_percent' in df.columns and pd.notna(row.get('change_percent')):
                    try:
                        pick['change_percent'] = float(row['change_percent'])
                    except:
                        pick['change_percent'] = 0
                
                # 添加行业
                if 'sector' in df.columns and pd.notna(row.get('sector')):
                    pick['sector'] = str(row['sector']).strip()
                
                picks.append(pick)
                count += 1
                
            except Exception as e:
                print(f"⚠️  处理行 {idx} 失败: {e}")
                continue
        
        print(f"✅ 成功生成 {len(picks)} 个AI选股推荐")
        return picks
        
    except Exception as e:
        print(f"❌ 生成AI选股失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_price_data_simple(df):
    """
    生成股价数据 - 简化版
    """
    print(f"\n📈 生成最新股价数据...")
    
    price_data = []
    
    for idx, row in df.iterrows():
        try:
            # 获取代码和名称
            code = row.get('code', '')
            name = row.get('name', '')
            
            if not code:
                continue
            
            # 创建基础对象
            stock = {
                'code': code,
                'name': str(name).strip() if pd.notna(name) else ''
            }
            
            # 添加其他字段
            for col in df.columns:
                if col in ['code', 'name']:
                    continue
                
                value = row[col]
                if pd.notna(value):
                    # 尝试转换为适当类型
                    try:
                        # 如果是数字
                        if isinstance(value, (int, float, np.integer, np.floating)):
                            stock[col] = float(value)
                        else:
                            # 尝试转换为float
                            try:
                                stock[col] = float(value)
                            except:
                                stock[col] = str(value).strip()
                    except:
                        stock[col] = str(value).strip()
            
            price_data.append(stock)
            
        except Exception as e:
            continue
    
    print(f"✅ 成功生成 {len(price_data)} 个股价数据")
    return price_data

def save_json(data, filepath):
    """保存JSON文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filepath)
        print(f"💾 保存: {filepath} ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"❌ 保存失败 {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("🏦 EOD CSV 转 JSON 生成器 v2.0")
    print("修复股票代码和生成逻辑")
    print("=" * 70)

    if len(sys.argv) != 2:
        print("用法: python generate_json_from_eod_fixed_v2.py <csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        sys.exit(1)

    # 加载数据
    df = load_eod_csv(csv_path)
    if df is None or df.empty:
        print("❌ 无法加载数据")
        sys.exit(1)

    # 标准化列名
    df = standardize_columns(df)

    # 生成AI选股
    ai_picks = generate_ai_picks_simple(df, top_n=20)

    # 生成股价数据
    price_data = generate_price_data_simple(df)

    # 获取日期信息
    filename = os.path.basename(csv_path)
    today = datetime.now().strftime('%Y-%m-%d')

    # 从文件名提取日期
    date_match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', filename)
    if date_match:
        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        date_str = today

    # 创建输出目录
    os.makedirs("history", exist_ok=True)

    # 1. 保存AI选股数据
    if ai_picks:
        picks_data = {
            "date": date_str,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source": filename,
            "total_picks": len(ai_picks),
            "picks": ai_picks
        }

        # Internal audit copy
        internal_history_file = f"history/picks_{date_str.replace('-', '')}.json"
        save_json(picks_data, internal_history_file)

        # Public web copy
        web_history_dir = "/storage/emulated/0/bursasearch/myx_shop/web/history"
        os.makedirs(web_history_dir, exist_ok=True)
        web_history_file = os.path.join(web_history_dir, f"picks_{date_str.replace('-', '')}.json")
        save_json(picks_data, web_history_file)

    # 2. 保存股价数据
    if price_data:
        price_json = {
            "date": date_str,
            "total_stocks": len(price_data),
            "stocks": price_data
        }
        save_json(price_json, "latest_price.json")

    # 3. 保存网页元数据
    web_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data_date": date_str,
        "total_stocks": len(price_data),
        "ai_picks_count": len(ai_picks)
    }
    save_json(web_data, "data.json")

    # 显示摘要
    print("\n" + "=" * 70)
    print("🎉 JSON文件生成完成！")
    print("=" * 70)
    print(f"📊 原始数据: {len(df)} 行")
    print(f"🎯 AI选股推荐: {len(ai_picks)} 个")
    print(f"📈 股价数据: {len(price_data)} 只股票")
    print(f"📅 数据日期: {date_str}")
    print("\n📁 生成的文件:")
    print("  • picks_latest.json     - AI选股推荐")
    print("  • latest_price.json     - 最新股价")
    print("  • data.json             - 网页元数据")
    if ai_picks:
        print(f"  • history/picks_{date_str.replace('-', '')}.json - 历史选股")
        print(f"  • web/history/picks_{date_str.replace('-', '')}.json - 前端选股")
    print("=" * 70)


if __name__ == "__main__":
    main()