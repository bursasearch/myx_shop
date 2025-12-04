#!/usr/bin/env python3
"""
直接修复股票API函数
"""

import re

# 读取原始文件
with open('api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 get_stock_data_yahoo 函数并替换
new_function = '''
def get_stock_data_yahoo(symbol, start_date, end_date=None):
    """直接从Yahoo Finance获取股票数据"""
    import requests
    import csv
    import io
    from datetime import datetime
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"获取股票数据: {symbol}, {start_date} 至 {end_date}")
    
    # 转换日期格式
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end_dt > datetime.now():
            end_dt = datetime.now()
            end_date = end_dt.strftime("%Y-%m-%d")
            
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt
            start_date, end_date = end_date, start_date
    
    except Exception as e:
        print(f"日期格式错误: {e}")
        return None
    
    # 马来西亚股票代码映射
    malaysia_map = {
        "1155": "MAYBANK.KL",
        "1295": "PBBANK.KL", 
        "6012": "TENAGA.KL",
        "5183": "PCHEM.KL",
        "1066": "RHBANK.KL",
        "1023": "CIMB.KL",
        "3034": "GENM.KL",
        "4715": "GENTING.KL"
    }
    
    # 尝试不同的符号格式
    symbols_to_try = []
    original_symbol = symbol
    
    # 1. 如果已经有.KL后缀
    if symbol.endswith('.KL'):
        symbols_to_try.append(symbol)
    
    # 2. 从映射表获取
    code = symbol.replace('.KL', '')
    if code in malaysia_map:
        symbols_to_try.append(malaysia_map[code])
    
    # 3. 尝试添加.KL
    symbols_to_try.append(f"{code}.KL")
    
    # 4. 尝试原始代码
    symbols_to_try.append(code)
    
    print(f"尝试的股票符号: {symbols_to_try}")
    
    for yf_symbol in symbols_to_try:
        try:
            # 方法1：使用 yfinance（如果已安装）
            try:
                import yfinance as yf
                print(f"使用 yfinance 尝试: {yf_symbol}")
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty:
                    prices = []
                    for date, row in df.iterrows():
                        prices.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "price": float(row["Close"])
                        })
                    print(f"yfinance 成功获取 {len(prices)} 个数据点")
                    return prices
            except Exception as e:
                print(f"yfinance 失败: {e}")
            
            # 方法2：使用 Yahoo Finance CSV API
            try:
                start_ts = int(start_dt.timestamp())
                end_ts = int(end_dt.timestamp())
                
                url = f"https://query1.finance.yahoo.com/v7/finance/download/{yf_symbol}?period1={start_ts}&period2={end_ts}&interval=1d&events=history&includeAdjustedClose=true"
                
                print(f"尝试URL: {url}")
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200 and "Date" in response.text:
                    csv_data = response.text
                    reader = csv.DictReader(io.StringIO(csv_data))
                    
                    prices = []
                    for row in reader:
                        if row.get("Adj Close") and row["Adj Close"] != "null":
                            try:
                                price = float(row["Adj Close"])
                                if price > 0:
                                    prices.append({
                                        "date": row["Date"],
                                        "price": price
                                    })
                            except:
                                continue
                    
                    if prices:
                        print(f"Yahoo CSV API 成功获取 {len(prices)} 个数据点")
                        return prices
                    
            except Exception as e:
                print(f"Yahoo CSV API 失败: {e}")
            
            # 方法3：使用 chart API
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "chart" in data and "result" in data["chart"]:
                        result = data["chart"]["result"][0]
                        timestamps = result.get("timestamp", [])
                        quotes = result.get("indicators", {}).get("quote", [{}])[0]
                        closes = quotes.get("close", [])
                        
                        prices = []
                        for i, timestamp in enumerate(timestamps):
                            if i < len(closes) and closes[i] is not None:
                                date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                                prices.append({
                                    "date": date_str,
                                    "price": closes[i]
                                })
                        
                        if prices:
                            print(f"Yahoo Chart API 成功获取 {len(prices)} 个数据点")
                            return prices
                            
            except Exception as e:
                print(f"Yahoo Chart API 失败: {e}")
                
        except Exception as e:
            print(f"尝试 {yf_symbol} 时失败: {e}")
            continue
    
    print(f"所有方法都失败，无法获取 {original_symbol} 的数据")
    return None
'''

# 替换函数
pattern = r'def get_stock_data_yahoo\(.*?\):.*?(?=\n\n|\ndef |\n@app\.|$)'
new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)

# 保存修复后的文件
with open('api.py.fixed', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已创建修复后的文件: api.py.fixed")
