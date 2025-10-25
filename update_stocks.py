#!/usr/bin/env python3
"""
AI選股資料自動更新腳本
使用說明: python update_stocks.py
"""

import json
import datetime
import random
import os
from pathlib import Path

class StockDataUpdater:
    def __init__(self, data_file='stock_data.json'):
        self.data_file = data_file
        self.stock_categories = ['科技股', '金融股', '新能源', '醫療股', '消費股']
        
    def load_existing_data(self):
        """載入現有資料"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "last_updated": "",
                "stocks": [],
                "update_history": []
            }
    
    def generate_realistic_performance(self, category, previous_performance=None):
        """生成真實的股價表現數據"""
        # 基礎波動範圍根據類別
        base_ranges = {
            '科技股': (-3, 8),
            '金融股': (-1, 4),
            '新能源': (-5, 12),
            '醫療股': (-2, 6),
            '消費股': (-1, 3)
        }
        
        min_change, max_change = base_ranges.get(category, (-2, 5))
        
        # 如果有之前的表現，基於之前數據做調整
        if previous_performance:
            previous_change = float(previous_performance.strip('%'))
            # 保持一定的連續性，但加入隨機波動
            new_change = previous_change + random.uniform(-2, 2)
            new_change = max(min_change, min(max_change, new_change))
        else:
            new_change = random.uniform(min_change, max_change)
            
        return f"{new_change:+.1f}%"
    
    def generate_ai_score(self, category, previous_score=None):
        """生成AI評分"""
        base_scores = {
            '科技股': (75, 95),
            '金融股': (80, 98),
            '新能源': (65, 85),
            '醫療股': (70, 90),
            '消費股': (75, 88)
        }
        
        min_score, max_score = base_scores.get(category, (70, 90))
        
        if previous_score:
            # 基於之前評分做小幅調整
            new_score = previous_score + random.randint(-3, 3)
            new_score = max(min_score, min(max_score, new_score))
        else:
            new_score = random.randint(min_score, max_score)
            
        return new_score
    
    def determine_risk_level(self, category, performance):
        """根據類別和表現確定風險等級"""
        performance_value = float(performance.strip('%'))
        
        risk_base = {
            '科技股': '中',
            '金融股': '低', 
            '新能源': '高',
            '醫療股': '中高',
            '消費股': '低'
        }
        
        base_risk = risk_base.get(category, '中')
        
        # 根據表現調整風險
        if performance_value > 10:
            if base_risk == '高': return '中高'
            elif base_risk == '中高': return '中'
        elif performance_value < -2:
            if base_risk == '低': return '中'
            elif base_risk == '中': return '中高'
            
        return base_risk
    
    def update_stock_data(self):
        """更新股票資料"""
        data = self.load_existing_data()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果沒有現有股票資料，初始化
        if not data["stocks"]:
            for category in self.stock_categories[:3]:  # 只使用前3個類別
                performance = self.generate_realistic_performance(category)
                ai_score = self.generate_ai_score(category)
                risk_level = self.determine_risk_level(category, performance)
                
                stock_data = {
                    "category": category,
                    "performance": performance,
                    "risk_level": risk_level,
                    "ai_score": ai_score,
                    "last_updated": current_time
                }
                data["stocks"].append(stock_data)
        else:
            # 更新現有資料
            for stock in data["stocks"]:
                previous_perf = stock["performance"]
                previous_score = stock["ai_score"]
                
                stock["performance"] = self.generate_realistic_performance(
                    stock["category"], previous_perf
                )
                stock["ai_score"] = self.generate_ai_score(
                    stock["category"], previous_score
                )
                stock["risk_level"] = self.determine_risk_level(
                    stock["category"], stock["performance"]
                )
                stock["last_updated"] = current_time
        
        data["last_updated"] = current_time
        data["update_history"].append({
            "timestamp": current_time,
            "action": "自動更新"
        })
        
        # 儲存更新後的資料
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 股票資料已更新於 {current_time}")
        self.print_current_data(data)
        
        return data
    
    def print_current_data(self, data):
        """打印當前資料"""
        print("\n📊 當前股票資料:")
        print("-" * 50)
        for stock in data["stocks"]:
            print(f"🏷️  {stock['category']}")
            print(f"   表現: {stock['performance']}")
            print(f"   風險: {stock['risk_level']}")
            print(f"   AI評分: {stock['ai_score']}/100")
            print()
    
    def manual_update_specific_stock(self, category, performance=None, ai_score=None):
        """手動更新特定股票"""
        data = self.load_existing_data()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for stock in data["stocks"]:
            if stock["category"] == category:
                if performance:
                    stock["performance"] = performance
                else:
                    stock["performance"] = self.generate_realistic_performance(
                        category, stock["performance"]
                    )
                
                if ai_score:
                    stock["ai_score"] = ai_score
                else:
                    stock["ai_score"] = self.generate_ai_score(
                        category, stock["ai_score"]
                    )
                
                stock["risk_level"] = self.determine_risk_level(
                    category, stock["performance"]
                )
                stock["last_updated"] = current_time
                
                data["last_updated"] = current_time
                data["update_history"].append({
                    "timestamp": current_time,
                    "action": f"手動更新 {category}"
                })
                
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {category} 已手動更新")
                return
        
        print(f"❌ 未找到 {category} 的資料")

def main():
    updater = StockDataUpdater()
    
    print("🤖 AI選股資料更新系統")
    print("=" * 40)
    
    while True:
        print("\n請選擇操作:")
        print("1. 自動更新所有股票資料")
        print("2. 手動更新特定股票")
        print("3. 顯示當前資料")
        print("4. 退出")
        
        choice = input("\n請輸入選擇 (1-4): ").strip()
        
        if choice == '1':
            updater.update_stock_data()
        elif choice == '2':
            category = input("請輸入股票類別 (科技股/金融股/新能源): ").strip()
            if category in ['科技股', '金融股', '新能源']:
                performance = input("表現 (直接按Enter使用自動生成): ").strip()
                ai_score = input("AI評分 (直接按Enter使用自動生成): ").strip()
                
                perf_value = performance if performance else None
                score_value = int(ai_score) if ai_score else None
                
                updater.manual_update_specific_stock(category, perf_value, score_value)
            else:
                print("❌ 無效的股票類別")
        elif choice == '3':
            data = updater.load_existing_data()
            updater.print_current_data(data)
        elif choice == '4':
            print("👋 再見！")
            break
        else:
            print("❌ 無效選擇")

if __name__ == "__main__":
    main()
