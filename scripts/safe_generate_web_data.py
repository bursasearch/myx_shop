#!/usr/bin/env python3
"""
安全版Web数据生成器 - 处理特殊列名
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import re

def safe_column_name(col_name):
    """将列名转换为安全的标识符"""
    if not isinstance(col_name, str):
        return str(col_name)
    
    # 替换特殊字符
    replacements = {
        ' ': '_',
        '(': '_',
        ')': '_',
        '*': '_star',
        '/': '_',
        '%': '_percent',
        '-': '_',
        '.': '_'
    }
    
    result = col_name.strip()
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # 移除多个下划线
    result = re.sub(r'_+', '_', result)
    result = re.sub(r'^_+|_+$', '', result)
    
    # 确保以字母开头
    if result and result[0].isdigit():
        result = 'col_' + result
    
    return result.lower()

def create_latest_price_json_from_normalized(normalized_csv_path, output_dir):
    """从规范化CSV创建latest_price.json"""
    print(f"📊 从 {os.path.basename(normalized_csv_path)} 创建latest_price.json")
    
    try:
        # 读取规范化CSV
        df = pd.read_csv(normalized_csv_path)
        print(f"  读取 {len(df)} 行数据，{len(df.columns)} 列")
        
        # 显示列名
        print("  原始列名:", list(df.columns))
        
        # 清理列名
        df.columns = [safe_column_name(col) for col in df.columns]
        print("  清理后列名:", list(df.columns))
        
        # 准备数据列表
        stocks = []
        
        # 映射列名
        column_mapping = {
            'code': 'code',
            'stock': 'name',
            'sector': 'sector',
            'last': 'last_price',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'prv_close': 'prev_close',
            'chg': 'change_percent',
            'vol': 'volume',
            'dy_star': 'dividend_yield',
            'b_percent': 'beta',
            'vol_ma_20': 'volume_ma_20',
            'rsi_14': 'rsi',
            'macd_26_12': 'macd',
            'eps_star': 'eps',
            'p_e': 'pe_ratio',
            'status': 'status'
        }
        
        for idx, row in df.iterrows():
            stock_data = {
                'code': str(row.get('code', '')).strip(),
                'name': str(row.get('stock', '')).strip(),
                'sector': str(row.get('sector', 'Unknown')).strip(),
                'last_price': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 0,
                'open': 0.0,
                'high': 0.0,
                'low': 0.0,
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            
            # 处理价格数据
            for source_col, target_key in column_mapping.items():
                if source_col in df.columns and pd.notna(row[source_col]):
                    try:
                        value = row[source_col]
                        
                        if target_key == 'last_price':
                            stock_data[target_key] = float(value)
                        elif target_key == 'change_percent':
                            # 处理Chg列（可能包含%符号）
                            chg_str = str(value).strip()
                            if chg_str and chg_str != '-':
                                chg_clean = chg_str.replace('%', '').replace('+', '')
                                stock_data[target_key] = float(chg_clean)
                        elif target_key == 'volume':
                            stock_data[target_key] = int(float(value))
                        elif target_key in ['open', 'high', 'low']:
                            stock_data[target_key] = float(value)
                        elif target_key in ['rsi', 'pe_ratio']:
                            stock_data[target_key] = float(value)
                    except Exception as e:
                        print(f"    警告: 处理列 {source_col} 时出错: {e}")
                        continue
            
            # 如果Chg列无法解析，尝试从价格计算
            if stock_data['change_percent'] == 0 and 'prev_close' in stock_data and stock_data['last_price'] > 0:
                try:
                    prev_close = float(stock_data.get('prev_close', stock_data['last_price']))
                    if prev_close > 0:
                        stock_data['change_percent'] = ((stock_data['last_price'] - prev_close) / prev_close) * 100
                        stock_data['change'] = stock_data['last_price'] - prev_close
                except:
                    pass
            
            stocks.append(stock_data)
        
        # 创建完整的数据结构
        data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_date': datetime.now().strftime('%Y-%m-%d'),
            'total_stocks': len(stocks),
            'market': 'Bursa Malaysia',
            'source_file': os.path.basename(normalized_csv_path),
            'stocks': stocks
        }
        
        # 保存JSON文件
        output_path = os.path.join(output_dir, 'latest_price.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建成功: {output_path}")
        print(f"   包含 {len(stocks)} 支股票数据")
        
        # 显示样本
        if stocks:
            sample = stocks[0]
            print(f"   样本: {sample['code']} - {sample['name']}: RM{sample['last_price']} ({sample['change_percent']}%)")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_picks_json_from_ai_data(normalized_csv_path, output_dir, top_n=15):
    """从规范化CSV创建AI选股JSON"""
    print(f"🎯 从规范化CSV创建选股推荐")
    
    try:
        df = pd.read_csv(normalized_csv_path)
        
        # 清理列名
        df.columns = [safe_column_name(col) for col in df.columns]
        
        # 简单选股逻辑
        picks = []
        
        # 1. 确保有必要的列
        required_columns = ['code', 'stock', 'last', 'chg', 'vol', 'sector']
        for col in required_columns:
            if col not in df.columns:
                print(f"  警告: 缺少列 {col}")
                df[col] = ''
        
        # 2. 计算Chg数值
        df['chg_numeric'] = df['chg'].apply(lambda x: 
            float(str(x).replace('%', '').replace('+', '').replace('-', '0')) 
            if str(x).replace('%', '').replace('+', '').replace('-', '').isdigit() 
            else 0.0
        )
        
        # 3. 简单评分算法
        def calculate_score(row):
            score = 50
            
            # 基于涨跌幅
            chg = row.get('chg_numeric', 0)
            if chg > 5:
                score += 20
            elif chg > 2:
                score += 10
            elif chg > 0:
                score += 5
            
            # 基于成交量
            vol = row.get('vol', 0)
            if vol > 1000000:
                score += 15
            elif vol > 100000:
                score += 10
            elif vol > 10000:
                score += 5
            
            # 基于RSI（如果有）
            if 'rsi_14' in row and pd.notna(row['rsi_14']):
                rsi = float(row['rsi_14'])
                if 30 < rsi < 70:
                    score += 5
                elif rsi < 30:
                    score += 10  # 超卖
                elif rsi > 70:
                    score -= 5   # 超买
            
            return max(0, min(100, score))
        
        df['score'] = df.apply(calculate_score, axis=1)
        
        # 4. 排序并选择前N个
        df_sorted = df.sort_values('score', ascending=False).head(top_n)
        
        # 5. 生成推荐
        for idx, row in enumerate(df_sorted.itertuples(), 1):
            code = str(getattr(row, 'code', '')).strip()
            name = str(getattr(row, 'stock', '')).strip()
            last_price = float(getattr(row, 'last', 0))
            chg = float(getattr(row, 'chg_numeric', 0))
            score = float(getattr(row, 'score', 50))
            volume = int(float(getattr(row, 'vol', 0)))
            sector = str(getattr(row, 'sector', 'Unknown')).strip()
            
            # 确定推荐级别
            if score >= 80:
                recommendation = "强力买入"
                risk_level = "低"
                color = "green"
            elif score >= 70:
                recommendation = "买入"
                risk_level = "中低"
                color = "lightgreen"
            elif score >= 60:
                recommendation = "考虑买入"
                risk_level = "中等"
                color = "yellow"
            else:
                recommendation = "观望"
                risk_level = "中高"
                color = "orange"
            
            # 判断是否为权证
            is_warrant = '-' in code or any(x in code for x in ['WA', 'WB', 'WC', 'WR'])
            instrument_type = "Warrant" if is_warrant else "Stock"
            
            pick = {
                'rank': idx,
                'code': code,
                'name': name,
                'instrument_type': instrument_type,
                'sector': sector,
                'current_price': last_price,
                'daily_change': chg,
                'score': score,
                'potential_score': int(score * 1.2 if score > 60 else score),
                'potential_reasons': f"AI评分{score}分，涨跌幅{chg}%" if chg != 0 else f"AI评分{score}分",
                'recommendation': recommendation,
                'risk_level': risk_level,
                'rsi': float(getattr(row, 'rsi_14', 50)) if hasattr(row, 'rsi_14') else 50.0,
                'volume': volume,
                'status': 'Active',
                'pe_ratio': float(getattr(row, 'p_e', 0)) if hasattr(row, 'p_e') else 0.0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            picks.append(pick)
        
        # 6. 创建JSON数据
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_picks': len(picks),
            'market': 'Bursa Malaysia',
            'source_file': os.path.basename(normalized_csv_path),
            'selection_criteria': '基于AI评分、涨跌幅和成交量的综合选股',
            'picks': picks
        }
        
        # 7. 保存文件
        output_path = os.path.join(output_dir, 'picks_latest.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 选股创建成功: {output_path}")
        print(f"   推荐 {len(picks)} 支股票")
        
        # 显示前3个推荐
        for i, pick in enumerate(picks[:3], 1):
            print(f"   {i}. {pick['code']} - {pick['name']}: 评分{pick['score']}, {pick['recommendation']}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 选股创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("="*60)
    print("🔄 安全版EOD数据转Web JSON生成器")
    print("="*60)
    
    # 配置路径
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
    WEB_DIR = os.path.join(BASE_DIR, "web")
    
    # 确保web目录存在
    os.makedirs(WEB_DIR, exist_ok=True)
    
    # 获取最新的规范化CSV文件
    normalized_dir = "./normalized_now"  # 您之前处理的输出目录
    if not os.path.exists(normalized_dir):
        print(f"❌ 规范化目录不存在: {normalized_dir}")
        print("请先运行EOD数据处理脚本")
        return
    
    # 找到最新的文件
    csv_files = [f for f in os.listdir(normalized_dir) if f.endswith('.csv')]
    if not csv_files:
        print("❌ 没有找到CSV文件")
        return
    
    # 按日期排序，获取最新的
    csv_files.sort(reverse=True)
    latest_csv = os.path.join(normalized_dir, csv_files[0])
    
    print(f"📁 使用文件: {os.path.basename(latest_csv)}")
    print(f"📂 输出目录: {WEB_DIR}")
    
    # 创建JSON文件
    print("\n" + "="*60)
    
    # 1. 创建latest_price.json
    print("📊 创建latest_price.json...")
    price_json = create_latest_price_json_from_normalized(latest_csv, WEB_DIR)
    
    # 2. 创建picks_latest.json
    print("\n🎯 创建picks_latest.json...")
    picks_json = create_picks_json_from_ai_data(latest_csv, WEB_DIR, top_n=15)
    
    print("\n" + "="*60)
    print("🎉 生成完成!")
    print("="*60)
    
    if price_json:
        print(f"✅ latest_price.json: {price_json}")
    if picks_json:
        print(f"✅ picks_latest.json: {picks_json}")
    
    print("\n📋 文件验证:")
    if price_json and os.path.exists(price_json):
        with open(price_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   latest_price.json: {data['total_stocks']} 支股票")
    
    if picks_json and os.path.exists(picks_json):
        with open(picks_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   picks_latest.json: {data['total_picks']} 个推荐")
    
    print("\n🌐 现在可以访问: retail-inv.html")
    print("="*60)

if __name__ == "__main__":
    main()
