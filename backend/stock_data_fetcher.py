#!/usr/bin/env python3
"""
可靠的股票数据获取模块 - 兼容GitHub部署
"""
import requests
import csv
import io
import random
from datetime import datetime, timedelta
from functools import lru_cache

class StockDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.malaysia_stocks = {
            '1155': {'name': 'MAYBANK', 'yahoo': '1155.KL', 'default_price': 8.92},
            '1295': {'name': 'PUBLIC BANK', 'yahoo': '1295.KL', 'default_price': 4.22},
            '6012': {'name': 'TENAGA', 'yahoo': '6012.KL', 'default_price': 11.50},
            '5183': {'name': 'PCHEM', 'yahoo': '5183.KL', 'default_price': 7.30},
        }
    
    @lru_cache(maxsize=100)
    def get_stock_data(self, stock_code, start_date, end_date=None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"获取股票数据: {stock_code}, {start_date} 至 {end_date}")
        
        stock_info = self.malaysia_stocks.get(stock_code, {
            'name': f'STOCK_{stock_code}',
            'yahoo': f'{stock_code}.KL',
            'default_price': 5.0
        })
        
        data = self._try_yfinance(stock_info['yahoo'], start_date, end_date)
        if data:
            return data
        
        data = self._try_yahoo_csv(stock_info['yahoo'], start_date, end_date)
        if data:
            return data
        
        data = self._try_yahoo_chart(stock_info['yahoo'], start_date, end_date)
        if data:
            return data
        
        print(f"使用模拟数据: {stock_code}")
        return self._generate_mock_data(stock_info, start_date, end_date)
    
    def _try_yfinance(self, symbol, start_date, end_date):
        try:
            import yfinance as yf
            print(f"尝试 yfinance: {symbol}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty:
                prices = []
                for date, row in df.iterrows():
                    prices.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'price': float(row['Close'])
                    })
                print(f"yfinance 成功: {len(prices)} 个数据点")
                return prices
        except Exception as e:
            print(f"yfinance 失败: {e}")
        return None
    
    def _try_yahoo_csv(self, symbol, start_date, end_date):
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            start_ts = int(start_dt.timestamp())
            end_ts = int(end_dt.timestamp())
            
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d&events=history"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and 'Date' in response.text:
                csv_data = response.text
                reader = csv.DictReader(io.StringIO(csv_data))
                prices = []
                for row in reader:
                    if row.get('Close') and row['Close'] != 'null':
                        try:
                            price = float(row['Close'])
                            if price > 0:
                                prices.append({
                                    'date': row['Date'],
                                    'price': price
                                })
                        except:
                            continue
                if prices:
                    print(f"Yahoo CSV 成功: {len(prices)} 个数据点")
                    return prices
        except Exception as e:
            print(f"Yahoo CSV 失败: {e}")
        return None
    
    def _try_yahoo_chart(self, symbol, start_date, end_date):
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            start_ts = int(start_dt.timestamp())
            end_ts = int(end_dt.timestamp())
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    timestamps = result.get('timestamp', [])
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]
                    closes = quotes.get('close', [])
                    
                    prices = []
                    for i, ts in enumerate(timestamps):
                        if i < len(closes) and closes[i] is not None:
                            date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            prices.append({
                                'date': date_str,
                                'price': closes[i]
                            })
                    
                    if prices:
                        print(f"Yahoo Chart 成功: {len(prices)} 个数据点")
                        return prices
        except Exception as e:
            print(f"Yahoo Chart 失败: {e}")
        return None
    
    def _generate_mock_data(self, stock_info, start_date, end_date):
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end_dt - start_dt).days
        if days <= 0:
            days = 30
        
        base_price = stock_info['default_price']
        current_price = base_price
        prices = []
        
        for i in range(days):
            date = (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            change = random.uniform(-0.5, 0.8)
            current_price = max(0.1, current_price * (1 + change/100))
            prices.append({
                'date': date,
                'price': round(current_price, 3)
            })
        
        print(f"生成模拟数据: {len(prices)} 个数据点")
        return prices

fetcher = StockDataFetcher()
