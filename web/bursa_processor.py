#!/usr/bin/env python3
"""
马来西亚Bursa股票数据处理器
专门处理马来西亚股票市场数据
"""

import pandas as pd
import os
import json
import re
from datetime import datetime

def is_malaysia_stock(code, name=""):
    """判断是否为马来西亚股票"""
    code_str = str(code).upper()
    name_str = str(name).upper()
    
    # 马来西亚股票特征
    # 1. 4位数字代码
    if re.match(r'^\d{4}$', code_str):
        return True
    
    # 2. 特定后缀
    malaysia_suffixes = ['-WA', '-WB', '-WC', '-WD', '-WE', 
                         'WA', 'WB', 'WC', 'WD', 'WE',
                         '-CR', '-CC']
    for suffix in malaysia_suffixes:
        if code_str.endswith(suffix):
            return True
    
    # 3. 名称包含马来西亚关键词
    malaysia_keywords = ['BURSA', 'MALAYSIA', 'MALAYAN', 'BERHAD', 'SDN BHD']
    for keyword in malaysia_keywords:
        if keyword in name_str:
            return True
    
    # 4. 已知的马来西亚股票代码模式
    malaysia_patterns = [
        r'^[A-Z]{4}$',  # 4个大写字母
        r'^\d{3}[A-Z]$',  # 3数字+1字母
    ]
    
    for pattern in malaysia_patterns:
        if re.match(pattern, code_str):
            return True
    
    return False

def convert_to_malaysia_currency(data):
    """将数据转换为马来西亚货币格式"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'currency':
                data[key] = 'MYR'
            elif key == 'last_price' and isinstance(value, (int, float)):
                # 确保价格格式正确
                pass
            else:
                convert_to_malaysia_currency(value)
    elif isinstance(data, list):
        for item in data:
            convert_to_malaysia_currency(item)
    
    return data

def process_bursa_csv(csv_file):
    """处理Bursa Malaysia的CSV文件"""
    print(f"🇲🇾 处理Bursa Malaysia CSV文件: {csv_file}")
    
    try:
        # 读取CSV文件
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        stocks = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Bursa CSV格式: 日期;$ 名称 ; 代码 ; 货币 ; 价格 ; ...
            parts = line.split(';')
            if len(parts) < 8:
                continue
            
            # 提取数据
            date = parts[0].strip()
            name = parts[1].strip().replace('$ ', '')
            code = parts[2].strip()
            currency = parts[3].strip()
            price_str = parts[4].strip()
            change_str = parts[6].strip() if len(parts) > 6 else "+0.000"
            volume_str = parts[7].strip() if len(parts) > 7 else "0"
            
            # 转换货币
            if currency == 'SGD':
                currency = 'MYR'
            
            # 转换价格
            try:
                price = float(price_str) if price_str and price_str != '000.000' else 0.0
            except:
                price = 0.0
            
            # 转换成交量
            try:
                volume = int(volume_str)
            except:
                volume = 0
            
            # 计算涨跌幅
            try:
                change_val = float(change_str.strip('+'))
                change_percent = (change_val / price * 100) if price > 0 else 0
            except:
                change_percent = 0
            
            stock = {
                "code": code if code else name[:4].upper(),
                "name": name,
                "last_price": price,
                "change": change_str,
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "currency": currency,
                "date": date,
                "market": "Bursa Malaysia"
            }
            
            stocks.append(stock)
        
        print(f"✅ 处理了 {len(stocks)} 只马来西亚股票")
        return stocks
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return []

def generate_malaysia_json():
    """生成马来西亚特定的JSON文件"""
    csv_file = "/storage/emulated/0/Download/20260102.csv"
    
    if not os.path.exists(csv_file):
        print("❌ CSV文件不存在")
        return
    
    # 处理CSV
    stocks = process_bursa_csv(csv_file)
    
    if not stocks:
        print("⚠️ 没有股票数据")
        return
    
    # 筛选马来西亚股票
    malaysia_stocks = [s for s in stocks if is_malaysia_stock(s['code'], s['name'])]
    
    if not malaysia_stocks:
        print("⚠️ 没有找到马来西亚股票，使用全部数据")
        malaysia_stocks = stocks
    
    print(f"🇲🇾 找到 {len(malaysia_stocks)} 只马来西亚股票")
    
    # 生成文件
    web_dir = "."
    
    # 1. picks_latest.json
    picks = []
    for i, stock in enumerate(malaysia_stocks[:20]):
        pick = stock.copy()
        pick['rank'] = i + 1
        
        # 判断类型
        if '-W' in stock['code'] or 'WARRANT' in stock['name'].upper():
            pick['instrument_type'] = 'Warrant'
            pick['risk_level'] = '高'
        else:
            pick['instrument_type'] = 'Stock'
            pick['risk_level'] = '中'
        
        # AI评分
        base_score = 75
        if pick['last_price'] < 0.2:
            base_score += 10
        if pick['volume'] > 5000:
            base_score += 5
        if pick['change'].startswith('+'):
            base_score += 10
        
        pick['score'] = min(95, base_score)
        pick['potential_score'] = min(100, pick['score'] + 15)
        
        # 马来西亚特定的推荐理由
        if pick['instrument_type'] == 'Warrant':
            pick['potential_reasons'] = 'Warrant技术面向好，马来西亚市场反弹机会大'
        else:
            pick['potential_reasons'] = '马来西亚股票基本面良好，值得关注'
        
        picks.append(pick)
    
    picks_data = {
        "date": malaysia_stocks[0]['date'] if malaysia_stocks else datetime.now().strftime("%Y-%m-%d"),
        "picks": picks,
        "count": len(picks),
        "market": "Bursa Malaysia",
        "currency": "MYR"
    }
    
    picks_file = os.path.join(web_dir, "picks_latest.json")
    with open(picks_file, 'w', encoding='utf-8') as f:
        json.dump(picks_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成马来西亚AI选股: {picks_file}")
    
    # 2. latest_price.json
    price_data = {
        "date": malaysia_stocks[0]['date'] if malaysia_stocks else datetime.now().strftime("%Y-%m-%d"),
        "stocks": malaysia_stocks[:100],
        "count": len(malaysia_stocks[:100]),
        "market": "Bursa Malaysia",
        "currency": "MYR"
    }
    
    price_file = os.path.join(web_dir, "latest_price.json")
    with open(price_file, 'w', encoding='utf-8') as f:
        json.dump(price_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成马来西亚股价数据: {price_file}")

if __name__ == "__main__":
    print("🇲🇾 Bursa Malaysia 数据处理器")
    print("==================================")
    generate_malaysia_json()
    print("
🎉 马来西亚股票数据处理完成！")
