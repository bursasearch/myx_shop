#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import csv
import io
from datetime import datetime, timedelta
import time
import os
import json
import random

# ===== 初始化 Flask 应用 =====
app = Flask(__name__)
CORS(app)

# ===== 数据获取函数 =====
_cache = {}

def get_stock_data(symbol, start_date, end_date=None):
    """获取股票数据，使用模拟数据"""
    symbol = symbol.upper()
    if not symbol.endswith('.KL'):
        symbol += '.KL'

    cache_key = f"{symbol}_{start_date}"
    if cache_key in _cache:
        return _cache[cache_key]

    print(f"🔍 开始获取 {symbol} 从 {start_date} 到 {end_date} 的数据")
    
    # 使用模拟数据
    prices = get_mock_data(symbol, start_date, end_date)
    if prices and len(prices) > 10:
        _cache[cache_key] = prices
        print(f"✅ {symbol} ← 模拟数据成功（{len(prices)} 天）")
        return prices

    print(f"💥 {symbol} 数据获取失败")
    return []

def get_mock_data(symbol, start_date, end_date):
    """提供模拟数据用于测试"""
    print(f"🎯 使用模拟数据 for {symbol}")
    
    # 模拟价格数据 - 马来西亚主要股票
    base_prices = {
        '1155.KL': {'start': 8.5, 'end': 9.2, 'name': 'MAYBANK'},
        '1295.KL': {'start': 4.1, 'end': 4.3, 'name': 'PUBLIC BANK'},
        '6012.KL': {'start': 11.2, 'end': 10.8, 'name': 'TENAGA'},
        '5183.KL': {'start': 6.8, 'end': 7.1, 'name': 'PCHEM'},
        '1066.KL': {'start': 5.5, 'end': 5.8, 'name': 'RHB BANK'},
        '4863.KL': {'start': 6.2, 'end': 6.0, 'name': 'TM'},
        '6888.KL': {'start': 2.8, 'end': 2.9, 'name': 'AXIATA'}
    }
    
    if symbol not in base_prices:
        # 默认模拟数据
        base_prices[symbol] = {'start': 1.0, 'end': 1.2, 'name': 'UNKNOWN'}
    
    start_price = base_prices[symbol]['start']
    end_price = base_prices[symbol]['end']
    stock_name = base_prices[symbol]['name']
    
    # 生成日期范围内的模拟数据
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    prices = []
    current_dt = start_dt
    days = (end_dt - start_dt).days
    
    # 确保至少有一些数据
    if days <= 0:
        days = 100  # 默认100天
    
    for i in range(days + 1):
        progress = i / days if days > 0 else 0
        # 添加一些随机波动
        fluctuation = random.uniform(-0.05, 0.05)
        current_price = start_price + (end_price - start_price) * progress + fluctuation
        # 确保价格为正数
        current_price = max(0.1, current_price)
        
        prices.append({
            'date': current_dt.strftime('%Y-%m-%d'),
            'price': round(current_price, 3)
        })
        current_dt += timedelta(days=1)
    
    print(f"📊 {stock_name} 生成 {len(prices)} 天模拟数据")
    print(f"   📈 价格范围: RM{prices[0]['price']} → RM{prices[-1]['price']}")
    return prices

# ===== 路由定义 =====

@app.route('/retail-inv')
def retail_inv():
    """散戶專用頁面"""
    try:
        with open('retail-inv.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading page: {str(e)}"

@app.route('/calc-profit', methods=['POST'])
def calc_profit():
    """計算單一股票收益"""
    try:
        data = request.json
        stock_code = data.get('stock_code', '1155').upper()
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date') or datetime.now().strftime('%Y-%m-%d')
        initial_investment = float(data.get('initial_investment', 10000))

        print(f"🧮 計算 {stock_code} 從 {start_date} 到 {end_date} 的收益")

        # 獲取股票數據
        prices = get_stock_data(stock_code, start_date, end_date)

        if not prices or len(prices) < 2:
            return jsonify({
                "success": False,
                "error": f"無法獲取 {stock_code} 的股票數據"
            })

        # 計算收益
        start_price = prices[0]['price']
        end_price = prices[-1]['price']

        shares = initial_investment / start_price
        final_value = shares * end_price
        profit_loss = final_value - initial_investment
        profit_loss_percent = (profit_loss / initial_investment) * 100

        # 計算持有天數
        start_dt = datetime.strptime(prices[0]['date'], '%Y-%m-%d')
        end_dt = datetime.strptime(prices[-1]['date'], '%Y-%m-%d')
        holding_days = (end_dt - start_dt).days

        print(f"💰 计算结果: 投资 RM{initial_investment} → RM{final_value:.2f} "
              f"({profit_loss_percent:+.2f}%)")

        return jsonify({
            "success": True,
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "initial_investment": initial_investment,
            "start_price": round(start_price, 3),
            "end_price": round(end_price, 3),
            "shares": round(shares, 2),
            "final_value": round(final_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percent": round(profit_loss_percent, 2),
            "holding_days": holding_days,
            "data_source": "模拟数据"
        })

    except Exception as e:
        print(f"💥 Error in calc_profit: {e}")
        return jsonify({
            "success": False,
            "error": f"計算錯誤: {str(e)}"
        })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/')
def index():
    return "Flask Server is Running! <a href='/retail-inv'>Go to Retail Investment Tool</a>"

# ===== 主程序 =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Flask server on port {port}...")
    print(f"Access the retail investment tool at: http://localhost:{port}/retail-inv")
    app.run(host='0.0.0.0', port=port, debug=True)
EOF