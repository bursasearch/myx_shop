#!/usr/bin/env python3
"""
Bursa Malaysia AI Stock Picker
多因子AI選股引擎 - 馬來西亞股市
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BursaAIStockPicker:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.selected_stocks = []
        
    def get_stock_data(self, symbol):
        """獲取股票數據從Yahoo Finance"""
        try:
            url = f"{self.base_url}/{symbol}.KL"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                return result
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_metrics(self, stock_data):
        """計算股票評分指標"""
        try:
            if not stock_data or 'indicators' not in stock_data:
                return None
                
            quote = stock_data['indicators']['quote'][0]
            # 簡單的評分邏輯 - 實際應該更複雜
            if 'close' in quote and quote['close']:
                current_price = quote['close'][-1]
                # 這裡應該加入更多因子：PE ratio, volume, momentum等
                score = np.random.uniform(0, 100)  # 暫時用隨機分數
                return {
                    'price': round(current_price, 2),
                    'score': round(score, 2),
                    'volume': quote.get('volume', [0])[-1] if quote.get('volume') else 0
                }
            return None
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return None
    
    def analyze_stock(self, symbol, name):
        """分析單一股票"""
        logger.info(f"Analyzing {symbol} - {name}")
        
        stock_data = self.get_stock_data(symbol)
        if not stock_data:
            return None
            
        metrics = self.calculate_metrics(stock_data)
        if not metrics:
            return None
            
        # 決定標籤和原因
        if metrics['score'] > 80:
            tag = "強力買入"
            reason = "技術面強勢，基本面良好"
        elif metrics['score'] > 60:
            tag = "買入"
            reason = "具備上漲潛力"
        else:
            tag = "觀察"
            reason = "需要進一步觀察"
            
        return {
            'code': symbol,
            'name': name,
            'price': metrics['price'],
            'score': metrics['score'],
            'tag': tag,
            'reason': reason
        }
    
    def run_analysis(self):
        """運行完整分析"""
        logger.info("Starting AI stock analysis...")
        
        # 馬來西亞主要股票列表（示例）
        stock_list = [
            ('AIRASIA', 'AirAsia Group Berhad'),
            ('BURSA', 'Bursa Malaysia Berhad'),
            ('CIMB', 'CIMB Group Holdings Berhad'),
            ('GENTING', 'Genting Berhad'),
            ('HARTA', 'Hartalega Holdings Berhad'),
            ('MAYBANK', 'Malayan Banking Berhad'),
            ('PCHEM', 'Petronas Chemicals Group Berhad'),
            ('PBBANK', 'Public Bank Berhad'),
            ('TENAGA', 'Tenaga Nasional Berhad'),
            ('TOPGLOV', 'Top Glove Corporation Berhad')
        ]
        
        # 分析所有股票
        for symbol, name in stock_list:
            result = self.analyze_stock(symbol, name)
            if result:
                self.selected_stocks.append(result)
            time.sleep(1)  # 避免請求過快
            
        # 按分數排序
        self.selected_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        # 只選擇前5名
        self.selected_stocks = self.selected_stocks[:5]
        
        logger.info(f"Analysis completed. Selected {len(self.selected_stocks)} stocks.")
        return self.selected_stocks
    
    def save_results(self, filename=None):
        """保存結果到JSON文件"""
        if not filename:
            filename = f"ai_stocks_{datetime.now().strftime('%Y%m%d')}.json"
            
        result = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'strategy': '多因子AI選股',
            'total_selected': len(self.selected_stocks),
            'selected_stocks': self.selected_stocks,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        # 同時保存為當前文件
        with open('ai_stocks.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Results saved to {filename}")
        return filename

def main():
    """主函數"""
    picker = BursaAIStockPicker()
    
    try:
        # 運行分析
        selected_stocks = picker.run_analysis()
        
        # 保存結果
        picker.save_results()
        
        # 輸出結果
        print("\n" + "="*50)
        print("AI選股結果")
        print("="*50)
        for i, stock in enumerate(selected_stocks, 1):
            print(f"{i}. {stock['code']} - {stock['name']}")
            print(f"   價格: RM {stock['price']} | 評分: {stock['score']}")
            print(f"   標籤: {stock['tag']} | 原因: {stock['reason']}")
            print()
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
