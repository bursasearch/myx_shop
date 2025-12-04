#!/bin/bash

# 修复 Yahoo Finance API 调用问题
echo "开始修复 Yahoo Finance API 问题..."

# 临时修改 api.py 中的 get_stock_data_yahoo 函数
sed -i '/def get_stock_data_yahoo/,/^def/ {
    /def get_stock_data_yahoo/,/^def/ {
        /def get_stock_data_yahoo/ {
            a\
def get_stock_data_yahoo(symbol, start_date, end_date=None):\
    """直接从Yahoo Finance获取股票数据 - 修复版"""\
    if end_date is None:\
        end_date = datetime.now().strftime("%Y-%m-%d")\
    \
    print(f"获取数据: {symbol}, {start_date} 至 {end_date}")\
    \
    # 尝试不同的数据源\
    # 方法1：使用 yfinance 库（如果可用）\
    try:\
        import yfinance as yf\
        print("使用 yfinance 库获取数据...")\
        ticker = yf.Ticker(symbol)\
        df = ticker.history(start=start_date, end=end_date)\
        if not df.empty:\
            prices = []\
            for date, row in df.iterrows():\
                prices.append({\
                    "date": date.strftime("%Y-%m-%d"),\
                    "price": float(row["Close"])\
                })\
            print(f"yfinance 成功获取 {len(prices)} 个数据点")\
            return prices\
    except Exception as e:\
        print(f"yfinance 失败: {e}")\
    \
    # 方法2：使用 Yahoo Finance v8 API\
    try:\
        import requests\
        import json\
        \
        # 转换为时间戳\
        from datetime import datetime\
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")\
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")\
        start_ts = int(start_dt.timestamp())\
        end_ts = int(end_dt.timestamp())\
        \
        # 使用新API\
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"\
        \
        headers = {\
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",\
            "Accept": "application/json"\
        }\
        \
        response = requests.get(url, headers=headers, timeout=30)\
        \
        if response.status_code == 200:\
            data = response.json()\
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:\
                result = data["chart"]["result"][0]\
                timestamps = result["timestamp"]\
                quotes = result["indicators"]["quote"][0]\
                \
                prices = []\
                for i in range(len(timestamps)):\
                    if quotes["close"][i] is not None:\
                        date_str = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")\
                        prices.append({\
                            "date": date_str,\
                            "price": quotes["close"][i]\
                        })\
                \
                print(f"Yahoo API 成功获取 {len(prices)} 个数据点")\
                return prices\
    except Exception as e:\
        print(f"Yahoo API 失败: {e}")\
    \
    # 方法3：使用 investpy 作为备用（需要安装）\
    try:\
        import investpy\
        print("尝试使用 investpy 获取马来西亚股票...")\
        \
        # 马来西亚股票映射\
        my_stocks = {\
            "1155": "Maybank",\
            "1295": "Public Bank",\
            "6012": "Tenaga Nasional",\
            "5183": "Petronas Chemicals"\
        }\
        \
        if symbol.replace(".KL", "") in my_stocks:\
            stock_name = my_stocks[symbol.replace(".KL", "")]\
            df = investpy.get_stock_historical_data(\
                stock=stock_name,\
                country="malaysia",\
                from_date=start_date,\
                to_date=end_date\
            )\
            \
            if not df.empty:\
                prices = []\
                for date, row in df.iterrows():\
                    prices.append({\
                        "date": date.strftime("%Y-%m-%d"),\
                        "price": float(row["Close"])\
                    })\
                print(f"investpy 成功获取 {len(prices)} 个数据点")\
                return prices\
    except Exception as e:\
        print(f"investpy 失败: {e}")\
    \
    print(f"所有数据源都失败: {symbol}")\
    return None
}' api.py
