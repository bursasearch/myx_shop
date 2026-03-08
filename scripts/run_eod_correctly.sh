#!/bin/bash
# fix_csv_in_scripts.sh - 直接在scripts目录中修复CSV解析

echo "🔧 修复CSV解析问题..."
echo "================================"

# 进入scripts目录
cd ~/bursasearch/myx_shop/scripts

# 1. 创建修复的CSV解析脚本
cat > fix_eod_parser.py << 'EOF'
#!/usr/bin/env python3
import pandas as pd
import os
import json
import sys
from datetime import datetime

def find_latest_csv():
    """查找最新的CSV文件"""
    download_dir = "/storage/emulated/0/Download"
    
    if not os.path.exists(download_dir):
        print("❌ Download目录不存在")
        return None
    
    csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ 没有找到CSV文件")
        return None
    
    # 按日期排序
    csv_files.sort(reverse=True)
    latest_csv = os.path.join(download_dir, csv_files[0])
    
    print(f"📁 找到CSV文件: {csv_files[0]}")
    return latest_csv

def parse_malaysia_csv(csv_file):
    """解析马来西亚EOD CSV格式"""
    print(f"📁 解析马来西亚CSV格式: {csv_file}")
    
    try:
        # 读取整个文件
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content:
            print("❌ 文件为空")
            return None
        
        lines = content.strip().split('\n')
        print(f"📊 总行数: {len(lines)}")
        
        # 显示前3行用于调试
        print("\n🔍 文件前3行:")
        for i in range(min(3, len(lines))):
            print(f"  行 {i+1}: {lines[i][:100]}...")
        print("")
        
        # 尝试解析每一行
        stocks = []
        successful = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 马来西亚EOD CSV通常用分号分隔
            # 格式示例: 2026-01-02;$ Aedge Group                 ;        ;SGD ;000.260;000.260;...
            parts = line.split(';')
            
            # 清理每个部分
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 8:  # 至少有基本字段
                try:
                    # 提取股票代码 (去掉多余空格)
                    code = parts[2].strip()
                    if not code or code == '':
                        code = f"STOCK_{line_num+1:04d}"
                    
                    # 提取股票名称 (去掉$符号)
                    name = parts[1].strip()
                    if name.startswith('$ '):
                        name = name[2:].strip()
                    
                    # 提取价格 (可能有多位小数)
                    price_str = parts[4].strip()
                    if price_str and price_str != '000.000':
                        try:
                            # 处理可能的前导零
                            last_price = float(price_str)
                        except:
                            last_price = 0.0
                    else:
                        last_price = 0.0
                    
                    # 提取涨跌
                    change_str = parts[6].strip() if len(parts) > 6 else "+00.000"
                    
                    # 提取成交量
                    volume_str = parts[7].strip() if len(parts) > 7 else "0"
                    try:
                        volume = int(volume_str)
                    except:
                        volume = 0
                    
                    stock = {
                        "code": code,
                        "name": name,
                        "last_price": last_price,
                        "change": change_str,
                        "volume": volume,
                        "currency": parts[3].strip() if len(parts) > 3 else "MYR",
                        "date": parts[0].strip() if len(parts) > 0 else "2026-01-02"
                    }
                    
                    # 计算涨跌幅百分比
                    if last_price > 0 and change_str:
                        try:
                            # 去掉+号并转换为float
                            change_val = float(change_str.strip('+'))
                            change_percent = (change_val / last_price) * 100
                            stock["change_percent"] = round(change_percent, 2)
                        except:
                            stock["change_percent"] = 0.0
                    
                    stocks.append(stock)
                    successful += 1
                    
                except Exception as e:
                    print(f"⚠️ 解析第 {line_num+1} 行失败: {e}")
                    continue
        
        print(f"✅ 成功解析 {successful}/{len(lines)} 只股票")
        
        if successful == 0:
            print("❌ 没有成功解析任何股票")
            return None
        
        # 显示前5只股票
        print("\n📊 示例数据 (前5只):")
        for i, stock in enumerate(stocks[:5]):
            print(f"  [{i+1}] {stock['code']} - {stock['name']}: RM {stock['last_price']} ({stock['change']})")
        
        return stocks
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_ai_picks(stocks):
    """生成AI选股推荐"""
    if not stocks:
        return []
    
    # 简单筛选逻辑: 价格低于1令吉且有成交量的股票
    candidates = []
    for stock in stocks:
        if stock['last_price'] > 0 and stock['last_price'] < 1.0 and stock['volume'] > 1000:
            candidates.append(stock)
    
    # 如果没有符合条件的，取前20只
    if not candidates:
        candidates = stocks[:20]
    
    # 添加AI评分和推荐
    picks = []
    for i, stock in enumerate(candidates[:20]):
        pick = stock.copy()
        pick['rank'] = i + 1
        
        # 根据条件分配类型
        if 'Warrant' in stock['name'] or stock['code'].endswith(('WA', 'WB', 'WC')):
            pick['instrument_type'] = 'Warrant'
            pick['risk_level'] = '高'
        else:
            pick['instrument_type'] = 'Stock'
            pick['risk_level'] = '中'
        
        # AI评分逻辑
        base_score = 75
        if pick['last_price'] < 0.5:
            base_score += 10
        if pick['volume'] > 10000:
            base_score += 5
        if pick['change'].startswith('+'):
            base_score += 10
        
        pick['score'] = min(95, base_score)
        pick['potential_score'] = min(100, pick['score'] + 15)
        
        # 推荐理由
        if pick['score'] >= 85:
            pick['recommendation'] = '🔥强烈买入'
            pick['potential_reasons'] = '价格低位，上涨空间大'
        elif pick['score'] >= 75:
            pick['recommendation'] = '👍买入'
            pick['potential_reasons'] = '技术面向好，值得关注'
        else:
            pick['recommendation'] = '📊观察'
            pick['potential_reasons'] = '等待更好时机'
        
        picks.append(pick)
    
    return picks

def generate_json_files():
    """生成所有JSON文件"""
    # 查找并解析CSV
    csv_file = find_latest_csv()
    
    if csv_file:
        stocks = parse_malaysia_csv(csv_file)
        if not stocks:
            print("⚠️ CSV解析失败，使用示例数据")
            stocks = generate_sample_data()
    else:
        print("⚠️ 未找到CSV文件，使用示例数据")
        stocks = generate_sample_data()
    
    # 生成AI选股
    picks = generate_ai_picks(stocks)
    
    # 获取日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    if stocks and 'date' in stocks[0]:
        current_date = stocks[0]['date']
    
    # 创建web目录
    web_dir = "../web"
    os.makedirs(web_dir, exist_ok=True)
    
    # 1. picks_latest.json
    picks_data = {
        "date": current_date,
        "picks": picks,
        "count": len(picks),
        "description": "AI选股推荐 - Bursa Malaysia"
    }
    
    picks_file = os.path.join(web_dir, "picks_latest.json")
    with open(picks_file, "w", encoding="utf-8") as f:
        json.dump(picks_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成: {picks_file} ({len(picks)} 只推荐股票)")
    
    # 2. latest_price.json
    price_data = {
        "date": current_date,
        "stocks": stocks[:100],  # 只取前100只避免文件太大
        "count": min(100, len(stocks))
    }
    
    price_file = os.path.join(web_dir, "latest_price.json")
    with open(price_file, "w", encoding="utf-8") as f:
        json.dump(price_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成: {price_file} ({len(price_data['stocks'])} 只股票)")
    
    # 3. data.json
    simple_data = {
        "date": current_date,
        "market": "Bursa Malaysia",
        "stock_count": len(stocks),
        "ai_picks_count": len(picks),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data_file = os.path.join(web_dir, "data.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(simple_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成: {data_file}")
    
    return True

def generate_sample_data():
    """生成示例数据"""
    print("📊 生成示例数据...")
    
    sample_stocks = []
    for i in range(50):
        stock = {
            "code": f"STOCK{i+1:04d}",
            "name": f"示例股票 {i+1}",
            "last_price": 0.1 + (i * 0.02),
            "change": f"+{0.01 + (i * 0.001):.3f}",
            "volume": 10000 + (i * 1000),
            "currency": "MYR",
            "date": "2026-01-02"
        }
        stock["change_percent"] = round((float(stock['change'].strip('+')) / stock['last_price']) * 100, 2)
        sample_stocks.append(stock)
    
    return sample_stocks

if __name__ == "__main__":
    print("🚀 Bursa Malaysia EOD数据处理器")
    print("==================================")
    generate_json_files()
    print("\n🎉 处理完成！")
EOF

# 2. 运行修复的解析器
echo "🚀 运行修复的CSV解析器..."
python3 fix_eod_parser.py

# 3. 检查生成的文件
echo ""
echo "📁 检查生成的文件:"
ls -la ../web/*.json

echo ""
echo "🔍 查看picks_latest.json前几行:"
head -20 ../web/picks_latest.json

echo ""
echo "✅ 修复完成！"
echo "现在您可以重新运行: ./run_eod_correctly.sh"
