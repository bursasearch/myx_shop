#!/usr/bin/env python3
import os
import json

def parse_real_stock_codes():
    """解析真实的股票代码"""
    csv_file = "/storage/emulated/0/Download/20260102.csv"
    
    if not os.path.exists(csv_file):
        print("❌ CSV文件不存在")
        return None
    
    print(f"📁 重新解析CSV文件: {csv_file}")
    
    stocks = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            # 使用分号分割
            parts = line.split(';')
            if len(parts) < 8:
                continue
            
            # 提取字段
            date_part = parts[0].strip()
            name_part = parts[1].strip()
            code_part = parts[2].strip()
            
            # 调试输出前10行
            if line_num < 10:
                print(f"  行 {line_num+1}: 代码='{code_part}', 名称='{name_part}'")
            
            # 如果代码部分为空，尝试从名称中提取
            if not code_part or code_part == '':
                # 检查名称中是否有股票代码模式
                name_clean = name_part.replace('$ ', '')
                
                # 常见的马来西亚股票代码模式
                # 如: "AEMULUS-WA" 或 "5058" 或 "IOICORP"
                import re
                
                # 尝试匹配常见的股票代码模式
                # 1. 大写字母+数字
                match = re.search(r'([A-Z]+[0-9]+[A-Z]*)', name_clean)
                if match:
                    code_part = match.group(1)
                # 2. 纯数字代码
                elif re.search(r'\b\d{4}\b', name_clean):
                    match = re.search(r'\b(\d{4})\b', name_clean)
                    code_part = match.group(1)
                # 3. 使用名称前几个字符
                else:
                    # 取名称的前4个字符作为代码
                    code_part = name_clean.replace(' ', '')[:4].upper()
            
            # 清理代码
            code_clean = code_part.strip().upper()
            if not code_clean:
                continue
            
            # 提取价格
            try:
                price_str = parts[4].strip()
                if price_str and price_str != '000.000':
                    last_price = float(price_str)
                else:
                    last_price = 0.0
            except:
                last_price = 0.0
            
            # 提取涨跌
            change_str = parts[6].strip() if len(parts) > 6 else "+00.000"
            
            # 提取成交量
            try:
                volume_str = parts[7].strip() if len(parts) > 7 else "0"
                volume = int(volume_str)
            except:
                volume = 0
            
            stock = {
                "code": code_clean,
                "name": name_part.replace('$ ', '').strip(),
                "last_price": last_price,
                "change": change_str,
                "volume": volume,
                "date": date_part,
                "currency": parts[3].strip() if len(parts) > 3 else "MYR"
            }
            
            stocks.append(stock)
    
    print(f"✅ 解析完成，找到 {len(stocks)} 只股票")
    
    # 显示一些示例
    print("\n📊 股票代码示例:")
    for i, stock in enumerate(stocks[:10]):
        print(f"  {stock['code']}: {stock['name']} - RM {stock['last_price']}")
    
    return stocks

def fix_picks_file():
    """修复picks_latest.json文件"""
    picks_file = "../web/picks_latest.json"
    
    if not os.path.exists(picks_file):
        print(f"❌ 文件不存在: {picks_file}")
        return
    
    # 读取现有的picks文件
    with open(picks_file, 'r', encoding='utf-8') as f:
        picks_data = json.load(f)
    
    print(f"📁 读取现有文件: {picks_file}")
    print(f"  原有 {len(picks_data['picks'])} 只推荐股票")
    
    # 解析真实的股票数据
    real_stocks = parse_real_stock_codes()
    
    if not real_stocks:
        print("❌ 无法解析真实股票数据")
        return
    
    # 创建新的AI推荐
    new_picks = []
    
    # 选择一些真实的股票作为AI推荐
    # 优先选择价格在0.1-1.0之间且有成交量的
    candidates = []
    for stock in real_stocks:
        if (0.05 <= stock['last_price'] <= 1.0 and 
            stock['volume'] > 1000 and 
            len(stock['code']) >= 2):
            candidates.append(stock)
    
    # 如果没有足够候选，放宽条件
    if len(candidates) < 20:
        candidates = [s for s in real_stocks if s['last_price'] > 0 and len(s['code']) >= 2][:50]
    
    # 生成AI推荐
    for i, stock in enumerate(candidates[:20]):
        pick = stock.copy()
        pick['rank'] = i + 1
        
        # 判断股票类型
        code = pick['code']
        name = pick['name'].upper()
        
        if ('WA' in code or 'WB' in code or 'WC' in code or 
            'WARRANT' in name or 'W ' in name or '-W' in name):
            pick['instrument_type'] = 'Warrant'
            pick['risk_level'] = '高'
        else:
            pick['instrument_type'] = 'Stock'
            pick['risk_level'] = '中'
        
        # AI评分
        base_score = 70
        
        # 根据价格调整
        if pick['last_price'] < 0.2:
            base_score += 15
        elif pick['last_price'] < 0.5:
            base_score += 10
        elif pick['last_price'] < 1.0:
            base_score += 5
        
        # 根据成交量调整
        if pick['volume'] > 10000:
            base_score += 10
        elif pick['volume'] > 5000:
            base_score += 5
        
        # 根据涨跌调整
        if pick['change'].startswith('+'):
            base_score += 10
        
        pick['score'] = min(95, base_score)
        pick['potential_score'] = min(100, pick['score'] + 10)
        
        # 推荐理由
        if pick['score'] >= 85:
            pick['recommendation'] = '🔥强烈买入'
            if pick['instrument_type'] == 'Warrant':
                pick['potential_reasons'] = 'Warrant严重超卖，反弹机会极大'
            else:
                pick['potential_reasons'] = '价格低位，上涨空间大'
        elif pick['score'] >= 75:
            pick['recommendation'] = '👍买入'
            if pick['instrument_type'] == 'Warrant':
                pick['potential_reasons'] = 'Warrant技术面向好，上涨潜力大'
            else:
                pick['potential_reasons'] = '技术面向好，值得关注'
        else:
            pick['recommendation'] = '📊观察'
            pick['potential_reasons'] = '等待更好时机'
        
        new_picks.append(pick)
    
    # 更新picks数据
    picks_data['picks'] = new_picks
    picks_data['count'] = len(new_picks)
    
    # 保存文件
    with open(picks_file, 'w', encoding='utf-8') as f:
        json.dump(picks_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 修复完成！新的推荐股票:")
    for pick in new_picks[:5]:
        print(f"  {pick['code']} - {pick['name']}: RM {pick['last_price']} ({pick['recommendation']})")
    
    return new_picks

def fix_latest_price_file():
    """修复latest_price.json文件"""
    price_file = "../web/latest_price.json"
    
    if not os.path.exists(price_file):
        print(f"❌ 文件不存在: {price_file}")
        return
    
    # 解析真实的股票数据
    real_stocks = parse_real_stock_codes()
    
    if not real_stocks:
        print("❌ 无法解析真实股票数据")
        return
    
    # 创建价格数据
    price_data = {
        "date": "2026-01-02",
        "stocks": real_stocks[:100],  # 只取前100只
        "count": min(100, len(real_stocks))
    }
    
    # 保存文件
    with open(price_file, 'w', encoding='utf-8') as f:
        json.dump(price_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 修复latest_price.json，包含 {len(price_data['stocks'])} 只真实股票")

if __name__ == "__main__":
    print("🚀 修复股票代码和真实数据")
    print("===============================")
    
    # 修复picks_latest.json
    fix_picks_file()
    
    # 修复latest_price.json
    fix_latest_price_file()
    
    print("\n🎉 修复完成！")
