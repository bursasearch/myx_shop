#!/usr/bin/env python3
"""
主數據更新腳本 - 整合所有步驟
"""
import subprocess
import os
import json
import schedule
import time
from datetime import date, timedelta
import sys

class DataPipeline:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.data_dir = os.path.join(self.base_dir, 'data')
        
        # 目錄路徑
        self.dirs = {
            'raw': os.path.join(self.data_dir, 'raw'),
            'normalized': os.path.join(self.data_dir, 'normalized'),
            'picks': os.path.join(self.data_dir, 'picks'),
            'audit': os.path.join(self.data_dir, 'audit'),
            'reports': os.path.join(self.data_dir, 'reports'),
            'logs': os.path.join(self.base_dir, 'logs')
        }
        
        # 創建所有目錄
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # 配置文件路徑
        self.config_file = os.path.join(self.config_dir, 'eod_config.json')
        self.sector_lookup_file = os.path.join(self.config_dir, 'sector_lookup.json')
        
        # 檢查配置文件是否存在
        if not os.path.exists(self.config_file):
            self.create_default_config()
    
    def create_default_config(self):
        """創建默認配置"""
        default_config = {
            "schema": [
                "Date",
                "Code",
                "Name", 
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Value",
                "Change",
                "Change%",
                "Sector Code",
                "Sector"
            ],
            "map": {
                "股票代碼": "Code",
                "名稱": "Name",
                "開盤": "Open",
                "最高": "High",
                "最低": "Low",
                "收盤": "Close",
                "成交量": "Volume",
                "成交值": "Value",
                "漲跌": "Change",
                "漲跌幅": "Change%",
                "行業代碼": "Sector Code"
            },
            "fill": {
                "Date": "-",
                "Sector": "Unknown"
            }
        }
        
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已創建默認配置: {self.config_file}")
    
    def run_pipeline(self, target_date=None):
        """運行完整數據流水線"""
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"🚀 運行數據流水線 - {date_str}")
        print(f"{'='*60}")
        
        # 步驟 1: 下載原始數據
        print("\n📥 步驟 1: 下載原始 EOD 數據")
        raw_file = self.download_raw_data(target_date)
        if not raw_file:
            print("❌ 下載失敗，跳過後續步驟")
            return False
        
        # 步驟 2: 標準化處理
        print("\n🔧 步驟 2: 標準化 EOD 數據")
        normalized_file = self.normalize_data(raw_file, target_date)
        if not normalized_file:
            print("❌ 標準化失敗，跳過後續步驟")
            return False
        
        # 步驟 3: 生成 AI 分析
        print("\n🤖 步驟 3: 生成 AI 推薦")
        picks_file = self.generate_picks(normalized_file, target_date)
        
        # 步驟 4: 更新最新推薦
        print("\n🔗 步驟 4: 更新最新推薦")
        if picks_file:
            self.update_latest_picks(picks_file)
        
        # 步驟 5: 更新日期索引
        print("\n📊 步驟 5: 更新日期索引")
        self.update_dates_index()
        
        print(f"\n✅ 流水線完成: {date_str}")
        return True
    
    def download_raw_data(self, target_date):
        """下載原始數據"""
        try:
            # 調用 download_eod.py
            download_script = os.path.join(self.base_dir, 'scripts', 'download_eod.py')
            
            if not os.path.exists(download_script):
                print("❌ download_eod.py 不存在")
                return None
            
            # 使用子進程運行
            result = subprocess.run(
                [sys.executable, download_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                date_str = target_date.strftime("%Y-%m-%d")
                raw_file = os.path.join(self.dirs['raw'], f"{date_str}_raw.csv")
                
                if os.path.exists(raw_file):
                    print(f"✅ 原始數據: {raw_file}")
                    return raw_file
                else:
                    print("❌ 原始文件未找到")
                    return None
            else:
                print(f"❌ 下載失敗: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 下載錯誤: {e}")
            return None
    
    def normalize_data(self, raw_file, target_date):
        """標準化數據"""
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            normalized_file = os.path.join(self.dirs['normalized'], f"{date_str}.csv")
            audit_file = os.path.join(self.dirs['audit'], f"{date_str}_audit.json")
            
            # 構建 normalize_eod.py 命令
            normalize_script = os.path.join(self.base_dir, 'scripts', 'normalize_eod.py')
            
            cmd = [
                sys.executable,
                normalize_script,
                raw_file,
                normalized_file,
                self.config_file,
                audit_file
            ]
            
            # 如果有行業映射文件，添加到配置
            if os.path.exists(self.sector_lookup_file):
                # 讀取行業映射並合併到配置
                with open(self.sector_lookup_file, 'r', encoding='utf-8') as f:
                    sector_lookup = json.load(f)
                
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                config['sector_lookup'] = sector_lookup
                
                # 創建臨時配置
                temp_config = os.path.join(self.dirs['logs'], 'temp_config.json')
                with open(temp_config, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                cmd[3] = temp_config  # 替換配置路徑
            
            # 運行標準化腳本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                print(f"✅ 標準化完成: {normalized_file}")
                
                # 檢查審計日誌
                if os.path.exists(audit_file):
                    with open(audit_file, 'r', encoding='utf-8') as f:
                        audit = json.load(f)
                    print(f"  處理記錄: {audit['rows_in']} -> {audit['rows_out']} 行")
                
                return normalized_file
            else:
                print(f"❌ 標準化失敗: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 標準化錯誤: {e}")
            return None
    
    def generate_picks(self, normalized_file, target_date):
        """生成 AI 推薦"""
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            
            # 運行 generate_picks.py
            picks_script = os.path.join(self.base_dir, 'scripts', 'generate_picks.py')
            
            cmd = [
                sys.executable,
                picks_script,
                '--date', date_str,
                '--input', normalized_file,
                '--output', self.dirs['picks']
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                picks_file = os.path.join(self.dirs['picks'], f"{date_str}.json")
                print(f"✅ AI 推薦生成: {picks_file}")
                return picks_file
            else:
                print(f"❌ AI 推薦生成失敗: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ AI 推薦錯誤: {e}")
            return None
    
    def update_latest_picks(self, picks_file):
        """更新最新推薦文件"""
        try:
            # 讀取生成的 JSON
            with open(picks_file, 'r', encoding='utf-8') as f:
                picks_data = json.load(f)
            
            # 添加額外信息
            picks_data['data_status'] = 'LIVE'
            picks_data['update_timestamp'] = time.time()
            picks_data['pipeline_version'] = '2.0'
            
            # 保存為 picks.json（前端使用）
            latest_file = os.path.join(self.base_dir, 'picks.json')
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(picks_data, f, ensure_ascii=False, indent=2)
            
            print(f"🔗 更新最新推薦: {latest_file}")
            
        except Exception as e:
            print(f"❌ 更新最新推薦失敗: {e}")
    
    def update_dates_index(self):
        """更新日期索引"""
        try:
            dates_script = os.path.join(self.base_dir, 'scripts', 'generate_dates_index.py')
            
            result = subprocess.run(
                [sys.executable, dates_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                print("✅ 日期索引更新完成")
            else:
                print(f"❌ 日期索引更新失敗: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 日期索引錯誤: {e}")
    
    def run_historical_pipeline(self, start_date, end_date):
        """運行歷史數據流水線"""
        current_date = start_date
        success_count = 0
        
        print(f"\n📅 處理歷史數據: {start_date} 至 {end_date}")
        
        while current_date <= end_date:
            # 跳過周末
            if current_date.weekday() < 5:
                print(f"\n處理 {current_date.strftime('%Y-%m-%d')}...")
                success = self.run_pipeline(current_date)
                if success:
                    success_count += 1
            
            current_date += timedelta(days=1)
            time.sleep(0.5)  # 避免過載
        
        print(f"\n🎉 歷史數據處理完成: {success_count} 天成功")
        return success_count
    
    def run_scheduler(self):
        """運行定時任務"""
        print("⏰ 啟動數據流水線定時任務...")
        print(f"  每日運行時間: 18:30 (收盤後)")
        print(f"  數據目錄: {self.data_dir}")
        
        # 設定定時任務
        schedule.every().day.at("18:30").do(self.run_pipeline)
        
        # 周一額外處理上周五數據
        schedule.every().monday.at("09:00").do(
            lambda: self.run_pipeline(date.today() - timedelta(days=3))
        )
        
        # 立即執行一次
        self.run_pipeline()
        
        # 保持運行
        while True:
            schedule.run_pending()
            time.sleep(60)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='運行數據流水線')
    parser.add_argument('--date', help='處理指定日期 (YYYY-MM-DD)')
    parser.add_argument('--historical', action='store_true', help='處理歷史數據')
    parser.add_argument('--start', help='歷史數據開始日期')
    parser.add_argument('--end', help='歷史數據結束日期')
    parser.add_argument('--daemon', action='store_true', help='運行守護進程')
    
    args = parser.parse_args()
    
    pipeline = DataPipeline()
    
    if args.daemon:
        # 運行守護進程模式
        pipeline.run_scheduler()
    
    elif args.historical:
        # 處理歷史數據
        start_date = date.fromisoformat(args.start) if args.start else date.today() - timedelta(days=30)
        end_date = date.fromisoformat(args.end) if args.end else date.today()
        
        pipeline.run_historical_pipeline(start_date, end_date)
    
    elif args.date:
        # 處理指定日期
        target_date = date.fromisoformat(args.date)
        pipeline.run_pipeline(target_date)
    
    else:
        # 處理今天
        pipeline.run_pipeline()
