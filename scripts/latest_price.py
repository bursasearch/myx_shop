#!/usr/bin/env python3
"""
創建乾淨的JSON文件
"""

import json
import datetime

def create_clean_latest_price():
    """創建乾淨的latest_price.json"""
    data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "total_stocks": 4,
        "market": "Bursa Malaysia",
        "stocks": [
            {
                "code": "7214",
                "name": "LII HEN INDUSTRIES",
                "last_price": 0.735,
                "change": 0.015,
                "change_percent": 2.08,
                "volume": 452100,
                "sector": "Industrial & Consumer Products",
                "open": 0.720,
                "high": 0.745,
                "low": 0.715,
                "last_updated": "15:30:22"
            },
            {
                "code": "7129",
                "name": "ASIA FILE CORPORATION",
                "last_price": 2.140,
                "change": 0.020,
                "change_percent": 0.94,
                "volume": 22400,
                "sector": "Industrial & Consumer Products",
                "open": 2.120,
                "high": 2.150,
                "low": 2.110,
                "last_updated": "15:31:15"
            }
        ],
        "summary": {
            "avg_change": 1.51,
            "top_gainers": [],
            "top_losers": [],
            "top_volume": []
        }
    }
    
    with open('../web/latest_price.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 創建乾淨的latest_price.json")

if __name__ == "__main__":
    create_clean_latest_price()