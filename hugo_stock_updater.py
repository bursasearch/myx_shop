#!/usr/bin/env python3
"""
Hugo專用AI選股資料更新腳本
目標路徑: ~/my-website/static/data/stock-data.json
"""

import json
import datetime
import random
import os
from pathlib import Path

class HugoStockUpdater:
    def __init__(self, hugo_static_path="~/my-website/static"):
        self.static_path = os.path.expanduser(hugo_static_path)
        self.data_dir = os.path.join(self.static_path, "data")
        self.data_file = os.path.join(self.data_dir, "stock-data.json")
        
        # 確保目錄存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Hugo專用股票配置
        self.stock_configs = {
            "tech": {
                "name": "科技股推薦",
                "icon": "💹",
                "base_range": (-2, 8),
                "base_score": (75, 95),
                "base_risk": "中"
            },
            "finance": {
                "name": "金融股分析", 
                "icon": "🏦",
                "base_range": (-1, 4),
                "base_score": (80, 98),
                "base_risk": "低"
            },
            "energy": {
                "name": "新能源趨勢",
                "icon": "⚡",
                "base_range": (-5, 12),
                "base_score": (65, 85),
                "base_risk": "高"
            }
        }
    
    def load_hugo_data(self):
        """載入Hugo靜態資料"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 初始化資料結構
            return {
                "last_updated": "",
                "update_count": 0,
                "stocks": [],
                "market_status": "正常交易",
                "update_history": []
            }
    
    def generate_stock_data(self, stock_key, previous_data=None):
        """生成單一股票資料"""
        config = self.stock_configs[stock_key]
        
        # 生成表現數據（更真實的算法）
        if previous_data:
            prev_perf = float(previous_data["performance"].strip('%'))
            # 基於前值 + 市場波動
            new_perf = prev_perf + random.uniform(-3, 5)
            new_perf = max(config["base_range"][0], min(config["base_range"][1], new_perf))
        else:
            new_perf = random.uniform(config["base_range"][0], config["base_range"][1])
        
        # 生成AI評分
        if previous_data:
            prev_score = previous_data["ai_score"]
            new_score = prev_score + random.randint(-2, 3)
            new_score = max(config["base_score"][0], min(config["base_score"][1], new_score))
        else:
            new_score = random.randint(config["base_score"][0], config["base_score"][1])
        
        # 動態風險評估
        performance_value = new_perf
        risk_level = config["base_risk"]
        if performance_value > 8:
            risk_level = "中低" if risk_level == "低" else "中"
        elif performance_value < -2:
            risk_level = "中高" if risk_level == "中" else "高"
        
        return {
            "id": stock_key,
            "name": config["name"],
            "icon": config["icon"],
            "performance": f"{new_perf:+.1f}%",
            "risk_level": risk_level,
            "ai_score": new_score,
            "trend": "up" if new_perf > 0 else "down"
        }
    
    def update_for_hugo(self):
        """為Hugo更新資料"""
        data = self.load_hugo_data()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"🔄 正在更新Hugo股票資料...")
        print(f"📁 目標路徑: {self.data_file}")
        
        # 初始化或更新股票資料
        if not data["stocks"]:
            # 首次初始化
            for stock_key in self.stock_configs.keys():
                stock_data = self.generate_stock_data(stock_key)
                data["stocks"].append(stock_data)
        else:
            # 更新現有資料
            for i, stock in enumerate(data["stocks"]):
                updated_data = self.generate_stock_data(stock["id"], stock)
                data["stocks"][i] = updated_data
        
        # 更新元數據
        data["last_updated"] = current_time
        data["update_count"] = data.get("update_count", 0) + 1
        data["market_status"] = "正常交易"  # 可以根據時間動態設定
        
        data["update_history"].append({
            "timestamp": current_time,
            "action": "自動更新",
            "version": f"v{data['update_count']}"
        })
        
        # 只保留最近10次記錄
        data["update_history"] = data["update_history"][-10:]
        
        # 寫入檔案
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Hugo資料更新完成！")
        print(f"📊 更新時間: {current_time}")
        print(f"🔢 總更新次數: {data['update_count']}")
        
        self.display_current_data(data)
        return data
    
    def display_current_data(self, data):
        """顯示當前資料"""
        print("\n📈 當前股票資料:")
        print("=" * 55)
        for stock in data["stocks"]:
            trend_icon = "📈" if stock["trend"] == "up" else "📉"
            print(f"{stock['icon']} {stock['name']}")
            print(f"   {trend_icon} 表現: {stock['performance']}")
            print(f"   🎯 風險: {stock['risk_level']}")
            print(f"   🤖 AI評分: {stock['ai_score']}/100")
            print()

def main():
    updater = HugoStockUpdater()
    
    print("🤖 Hugo AI選股資料更新系統")
    print("=" * 50)
    
    try:
        data = updater.update_for_hugo()
        
        # 自動觸發Hugo重建（可選）
        print("\n🎯 下一步操作:")
        print("1. 資料已保存到 static/data/stock-data.json")
        print("2. 在Hugo頁面中訪問: /data/stock-data.json") 
        print("3. 執行 'hugo server' 預覽更改")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        print("💡 請檢查Hugo目錄路徑是否正確")

if __name__ == "__main__":
    main()
