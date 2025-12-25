#!/usr/bin/env python3
"""
专门为您的规范化EOD数据生成web JSON文件
用于 retail-inv.html
"""

import os
import json
import pandas as pd
from datetime import datetime
import numpy as np

def create_latest_price_json(normalized_csv_path, output_dir):
    """从规范化CSV创建latest_price.json"""
    print(f"📊 从 {normalized_csv_path} 创建latest_price.json")
    
    try:
        # 读取规范化CSV
        df = pd.read_csv(normalized_csv_path)
        print(f"  读取 {len(df)} 行数据")
        
        # 准备数据列表
        stocks = []
        
        for idx, row in df.iterrows():
            # 清理和处理数据
            code = str(row.get('Code', '')).strip()
            name = str(row.get('Stock', '')).strip()
            sector = str(row.get('Sector', 'Unknown')).strip()
            
            # 处理价格数据
            last_price = float(row.get('Last', 0)) if pd.notna(row.get('Last')) else 0
            open_price = float(row.get('Open', 0)) if pd.notna(row.get('Open')) else 0
            high = float(row.get('High', 0)) if pd.notna(row.get('High')) else 0
            low = float(row.get('Low', 0)) if pd.notna(row.get('Low')) else 0
            
            # 处理涨跌幅（您的Chg列已经是百分比）
            chg_str = str(row.get('Chg', '0%')).strip()
            chg_percent = 0.0
            chg_value = 0.0
            
            if chg_str and chg_str != '-':
                # 移除百分比符号，转换为数字
                chg_clean = chg_str.replace('%', '')
                try:
                    chg_percent = float(chg_clean)
                    # 计算涨跌值
                    prev_close = float(row.get('Prv Close', last_price))
                    chg_value = (chg_percent / 100) * prev_close
                except:
                    chg_percent = 0.0
                    chg_value = 0.0
            
            # 处理成交量
            volume = int(row.get('Vol', 0)) if pd.notna(row.get('Vol')) else 0
            
            # 其他指标
            dividend_yield = str(row.get('DY*', '-')).strip()
            beta = str(row.get('B%', '-')).strip()
            volume_ma_20 = int(row.get('Vol MA (20)', 0)) if pd.notna(row.get('Vol MA (20)')) else 0
            rsi = float(row.get('RSI (14)', 0)) if pd.notna(row.get('RSI (14)')) else 0
            macd = str(row.get('MACD (26, 12)', '-')).strip()
            eps = str(row.get('EPS*', '-')).strip()
            pe_ratio = float(row.get('P/E', 0)) if pd.notna(row.get('P/E')) else 0
            status = str(row.get('Status', 'Active')).strip()
            
            stock_data = {
                'code': code,
                'name': name,
                'last_price': last_price,
                'change': chg_value,  # 涨跌值
                'change_percent': chg_percent,  # 涨跌幅
                'volume': volume,
                'sector': sector,
                'open': open_price,
                'high': high,
                'low': low,
                'volume_ma_20': volume_ma_20,
                'rsi': rsi,
                'macd': macd,
                'eps': eps,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield,
                'beta': beta,
                'status': status,
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            
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
        
        return output_path
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_simple_picks_json(normalized_csv_path, output_dir, top_n=20):
    """创建简化的选股JSON"""
    print(f"🎯 创建选股推荐")
    
    try:
        df = pd.read_csv(normalized_csv_path)
        
        # 简单的选股逻辑
        # 1. 过滤掉状态不是Active的
        if 'Status' in df.columns:
            df = df[df['Status'] == 'Active']
        
        # 2. 根据涨跌幅排序
        df['Chg_Numeric'] = df['Chg'].apply(lambda x: float(str(x).replace('%', '').replace('-', '0')) if str(x).replace('%', '').replace('-', '').isdigit() else 0)
        
        # 3. 根据成交量过滤
        if 'Vol' in df.columns:
            df = df[df['Vol'] > 1000]  # 最低成交量
        
        # 4. 根据涨跌幅和成交量综合评分
        if 'Chg_Numeric' in df.columns and 'Vol' in df.columns:
            df['Score'] = df['Chg_Numeric'] * 0.7 + np.log10(df['Vol'] + 1) * 0.3
        
        # 5. 排序并选择前N个
        df_sorted = df.sort_values('Score', ascending=False).head(top_n)
        
        picks = []
        for idx, row in df_sorted.iterrows():
            pick = {
                'rank': idx + 1,
                'code': str(row.get('Code', '')).strip(),
                'name': str(row.get('Stock', '')).strip(),
                'sector': str(row.get('Sector', 'Unknown')).strip(),
                'current_price': float(row.get('Last', 0)) if pd.notna(row.get('Last')) else 0,
                'daily_change': float(row.get('Chg_Numeric', 0)),
                'volume': int(row.get('Vol', 0)) if pd.notna(row.get('Vol')) else 0,
                'rsi': float(row.get('RSI (14)', 0)) if pd.notna(row.get('RSI (14)')) else 0,
                'pe_ratio': float(row.get('P/E', 0)) if pd.notna(row.get('P/E')) else 0,
                'reason': '涨势良好，成交量活跃' if float(row.get('Chg_Numeric', 0)) > 0 else '技术指标显示潜力'
            }
            picks.append(pick)
        
        # 创建数据
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_picks': len(picks),
            'selection_criteria': '基于涨跌幅和成交量的简单选股',
            'picks': picks
        }
        
        # 保存文件
        output_path = os.path.join(output_dir, 'picks_latest.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 选股创建成功: {output_path}")
        print(f"   推荐 {len(picks)} 支股票")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 选股创建失败: {e}")
        return None

def main():
    """主函数"""
    print("="*60)
    print("🔄 EOD数据转Web JSON生成器")
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
    
    print(f"📁 使用文件: {latest_csv}")
    print(f"📂 输出目录: {WEB_DIR}")
    
    # 创建JSON文件
    print("\n" + "="*60)
    
    # 1. 创建latest_price.json
    price_json = create_latest_price_json(latest_csv, WEB_DIR)
    
    # 2. 创建picks_latest.json
    picks_json = create_simple_picks_json(latest_csv, WEB_DIR, top_n=15)
    
    print("\n" + "="*60)
    print("🎉 生成完成!")
    print("="*60)
    
    if price_json:
        print(f"✅ latest_price.json: {price_json}")
    if picks_json:
        print(f"✅ picks_latest.json: {picks_json}")
    
    print("\n📋 文件内容示例:")
    if price_json and os.path.exists(price_json):
        with open(price_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   latest_price.json: {data['total_stocks']} 支股票")
            if data['stocks']:
                sample = data['stocks'][0]
                print(f"   示例: {sample['code']} - {sample['name']}: {sample['last_price']} ({sample['change_percent']}%)")
    
    print("\n🌐 现在可以访问: retail-inv.html")
    print("="*60)

if __name__ == "__main__":
    main()
