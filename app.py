from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import json
from datetime import datetime, timedelta
import shutil
import requests
import csv
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_stock_data_yahoo(symbol, start_date, end_date=None):
    """直接從Yahoo Finance獲取股票數據"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 轉換日期格式
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    # 構建URL
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_timestamp}&period2={end_timestamp}&interval=1d&events=history&includeAdjustedClose=true"
    
    try:
        print(f"獲取數據: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析CSV數據
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        
        prices = []
        for row in reader:
            if row['Adj Close'] and row['Adj Close'] != 'null':
                prices.append({
                    'date': row['Date'],
                    'price': float(row['Adj Close'])
                })
        
        print(f"成功獲取 {symbol}: {len(prices)} 個數據點")
        return prices
        
    except Exception as e:
        print(f"獲取 {symbol} 數據失敗: {e}")
        return None

@app.route('/run-backtest', methods=['POST'])
def run_backtest():
    """運行真實回測"""
    try:
        data = request.json
        stocks = data.get('stocks', [])
        start_date = data.get('start_date')
        capital = data.get('capital', 100000)
        
        if not stocks or not start_date:
            return jsonify({'success': False, 'error': '缺少必要參數'})
        
        print(f"開始回測: {stocks}, 開始日期: {start_date}, 資金: {capital}")
        
        # 獲取股票數據
        stock_data = {}
        valid_stocks = []
        
        for stock_code in stocks:
            try:
                # 處理股票代碼格式
                if not stock_code.endswith('.KL'):
                    yf_symbol = stock_code + '.KL'
                else:
                    yf_symbol = stock_code
                
                print(f"獲取 {yf_symbol} 數據...")
                
                # 直接從Yahoo Finance獲取數據
                prices = get_stock_data_yahoo(yf_symbol, start_date)
                
                if not prices:
                    print(f"無法獲取 {yf_symbol} 的數據")
                    continue
                
                stock_data[yf_symbol] = prices
                valid_stocks.append(yf_symbol)
                print(f"成功獲取 {yf_symbol}: {len(prices)} 個數據點")
                
            except Exception as e:
                print(f"獲取 {stock_code} 數據時出錯: {e}")
                continue
        
        if not valid_stocks:
            return jsonify({'success': False, 'error': '無法獲取任何股票數據'})
        
        # 添加大盤基準
        try:
            print("獲取 KLCI 大盤數據...")
            klse_prices = get_stock_data_yahoo('^KLSE', start_date)
            if klse_prices:
                stock_data['^KLSE'] = klse_prices
                valid_stocks.append('^KLSE')
                print(f"成功獲取 KLCI 大盤數據: {len(klse_prices)} 個數據點")
        except Exception as e:
            print(f"獲取 KLCI 數據時出錯: {e}")
        
        # 計算回測結果
        result = calculate_backtest(stock_data, valid_stocks, capital)
        result['success'] = True
        result['valid_stocks'] = valid_stocks
        
        print("回測完成")
        return jsonify(result)
        
    except Exception as e:
        print(f"回測過程出錯: {e}")
        return jsonify({'success': False, 'error': str(e)})

def calculate_backtest(stock_data, valid_stocks, capital):
    """計算回測結果"""
    # 找到共同交易日
    common_dates = None
    for symbol in valid_stocks:
        if symbol == '^KLSE':
            continue
        dates = [p['date'] for p in stock_data[symbol]]
        if common_dates is None:
            common_dates = set(dates)
        else:
            common_dates = common_dates.intersection(set(dates))
    
    if not common_dates:
        return {'error': '沒有共同的交易日'}
    
    common_dates = sorted(list(common_dates))
    print(f"共同交易日數量: {len(common_dates)}")
    
    # 組合淨值計算（等權重）
    portfolio = [capital]
    current_value = capital
    peak = capital
    
    stock_symbols = [s for s in valid_stocks if s != '^KLSE']
    
    for i in range(1, len(common_dates)):
        date = common_dates[i]
        prev_date = common_dates[i-1]
        
        total_return = 0
        valid_count = 0
        
        for symbol in stock_symbols:
            # 找到當前和前一交易日的價格
            current_price_obj = next((p for p in stock_data[symbol] if p['date'] == date), None)
            prev_price_obj = next((p for p in stock_data[symbol] if p['date'] == prev_date), None)
            
            if current_price_obj and prev_price_obj and prev_price_obj['price'] > 0:
                daily_return = current_price_obj['price'] / prev_price_obj['price']
                total_return += daily_return
                valid_count += 1
        
        if valid_count > 0:
            avg_return = total_return / valid_count
            current_value *= avg_return
            portfolio.append(current_value)
            peak = max(peak, current_value)
        else:
            portfolio.append(portfolio[-1])
    
    # 大盤基準計算
    benchmark = [100]
    bench_value = 100
    
    if '^KLSE' in stock_data:
        klse_prices = stock_data['^KLSE']
        for i in range(1, len(common_dates)):
            date = common_dates[i]
            prev_date = common_dates[i-1]
            
            current_price = next((p['price'] for p in klse_prices if p['date'] == date), None)
            prev_price = next((p['price'] for p in klse_prices if p['date'] == prev_date), None)
            
            if current_price and prev_price and prev_price > 0:
                bench_value *= current_price / prev_price
            benchmark.append(bench_value)
    
    # 計算指標
    total_return_pct = ((portfolio[-1] / capital) - 1) * 100
    days = (datetime.strptime(common_dates[-1], '%Y-%m-%d') - datetime.strptime(common_dates[0], '%Y-%m-%d')).days
    annual_return_pct = (pow(portfolio[-1] / capital, 365 / days) - 1) * 100 if days > 0 else 0
    
    # 計算最大回撤
    max_drawdown = 0
    for i in range(len(portfolio)):
        current_peak = max(portfolio[:i+1])
        drawdown = ((current_peak - portfolio[i]) / current_peak) * 100
        max_drawdown = max(max_drawdown, drawdown)
    
    return {
        'portfolio': portfolio,
        'benchmark': benchmark,
        'dates': common_dates,
        'metrics': {
            'total_return': total_return_pct,
            'annual_return': annual_return_pct,
            'max_drawdown': max_drawdown,
            'final_value': portfolio[-1]
        }
    }

# 其他現有路由保持不變...
@app.route('/run-ai-selection', methods=['POST'])
def run_ai_selection():
    """運行AI選股腳本"""
    try:
        if os.path.exists('ai_stocks.json'):
            shutil.copy('ai_stocks.json', 'ai_stocks_last_week.json')
        
        result = subprocess.run(
            ['python', 'bursa_ai_stock_picker.py'], 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            timeout=300
        )
        
        if result.returncode == 0:
            with open('ai_stocks.json', 'r', encoding='utf-8') as f:
                stock_data = json.load(f)
                
            return jsonify({
                'status': 'success', 
                'output': result.stdout,
                'stocks_selected': len(stock_data.get('selected_stocks', [])),
                'analysis_date': stock_data.get('analysis_date', 'N/A')
            })
        else:
            return jsonify({
                'status': 'error', 
                'output': result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

@app.route('/get-stocks/<type>')
def get_stocks(type):
    """獲取選股數據"""
    try:
        if type == 'current':
            filename = 'ai_stocks.json'
        elif type == 'last_week':
            filename = 'ai_stocks_last_week.json'
        else:
            return jsonify({'error': 'Invalid type'}), 400
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        formatted_data = {
            'analysis_date': data.get('analysis_date', 'N/A'),
            'strategy': data.get('strategy', '多因子AI選股'),
            'total_selected': len(data.get('selected_stocks', [])),
            'selected_stocks': data.get('selected_stocks', []),
            'timestamp': data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
            
        return jsonify(formatted_data)
        
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """健康檢查"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)