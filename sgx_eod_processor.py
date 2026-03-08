#!/usr/bin/env python3
"""
SGX EOD Data Processor
处理新加坡交易所EOD数据，去除Penny Stocks，计算涨跌幅，生成JSON
根据实际数据格式（17个字段）- 修改為只輸出 top 10 股票
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import argparse

# ==================== 配置参数 ====================
PENNY_THRESHOLD = 0.20  # 去除股价低于 SGD 0.20 的股票
MIN_VOLUME = 10000      # 最小成交量（股）
TOP_N = 10              # 只選出前10支股票

# 实际SGX数据字段（17个字段）- 根据实际数据推断
SGX_COLUMNS = [
    'DATE',              # 0: 交易日期 (YYYY-MM-DD)
    'NAME',              # 1: 股票名稱 (可能有前綴符號)
    'SUSP',              # 2: 停牌標記 (SUSP 或空白)
    'CURRENCY',          # 3: 貨幣 (SGD)
    'HIGH',              # 4: 最高價
    'LOW',               # 5: 最低價
    'LAST',              # 6: 最新價
    'CHANGE',            # 7: 變動
    'VOLUME',            # 8: 成交量
    'BID',               # 9: 買入價
    'OFFER',             # 10: 賣出價
    'MARKET',            # 11: 市場/板塊
    'OPEN',              # 12: 開盤價
    'VALUE',             # 13: 成交額
    'STOCK_CODE',        # 14: 股票代碼
    'DCLOSE',            # 15: 前收盤價
    'EXTRA'              # 16: 額外欄位（可能為空）
]

# 需要转换为数值的字段
NUMERIC_COLUMNS = ['HIGH', 'LOW', 'LAST', 'CHANGE', 'BID', 'OFFER', 'OPEN', 'DCLOSE', 'VOLUME', 'VALUE']

class SGXEODProcessor:
    def __init__(self, threshold=PENNY_THRESHOLD, min_volume=MIN_VOLUME):
        self.threshold = threshold
        self.min_volume = min_volume
        self.stats = {
            'total': 0,
            'suspended_removed': 0,
            'penny_removed': 0,
            'low_volume_removed': 0,
            'final': 0
        }
    
    def parse_sgx_dat(self, file_path):
        """解析SGX的.dat文件"""
        print(f"📂 读取文件: {file_path}")
        
        try:
            # 讀取文件，指定分隔符為分號
            df = pd.read_csv(
                file_path, 
                sep=';', 
                names=SGX_COLUMNS, 
                encoding='utf-8',
                skipinitialspace=True,
                on_bad_lines='warn',
                dtype=str  # 先全部讀取為字符串
            )
            
            print(f"✅ 读取成功，共 {len(df)} 行，{len(df.columns)} 欄位")
            return df
            
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clean_data(self, df):
        """数据清洗和类型转换"""
        print("🧹 清洗数据...")
        
        # 记录原始数量
        self.stats['total'] = len(df)
        
        # 创建副本避免警告
        df_clean = df.copy()
        
        # 去除所有欄位的前後空格
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # 轉換數值欄位 - 處理 SGX 的格式 (如 '000.390' -> 0.39)
        for col in NUMERIC_COLUMNS:
            if col in df_clean.columns:
                # 先去除前導零
                df_clean[col] = df_clean[col].str.replace(r'^0+', '', regex=True)
                # 轉換為浮點數
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 處理股票名稱，去除前綴符號（$, #, +, ^ 等）
        df_clean['NAME'] = df_clean['NAME'].str.replace(r'^[\$\#\+\^\&]', '', regex=True).str.strip()
        
        # 處理股票代碼
        df_clean['STOCK_CODE'] = df_clean['STOCK_CODE'].str.strip()
        
        # 判斷是否停牌：SUSP 欄位包含 'SUSP' 表示停牌
        df_clean['IS_SUSPENDED'] = df_clean['SUSP'].str.upper().str.contains('SUSP', na=False)
        
        # 過濾掉無效數據（股價為空或為0）
        df_clean = df_clean[df_clean['LAST'].notna() & (df_clean['LAST'] > 0)]
        
        if len(df_clean) == 0:
            print("⚠️ 沒有有效股價數據")
            return df_clean
        
        # 計算前收盤價和漲跌幅百分比
        # 如果 CHANGE 為空，嘗試用 LAST - DCLOSE 計算
        df_clean['CHANGE'] = df_clean['CHANGE'].fillna(df_clean['LAST'] - df_clean['DCLOSE'])
        
        # 計算前收盤價
        df_clean['PREV_CLOSE'] = df_clean['LAST'] - df_clean['CHANGE']
        
        # 避免除零錯誤
        mask = df_clean['PREV_CLOSE'] > 0
        df_clean.loc[mask, 'CHANGE_PERCENT'] = (df_clean.loc[mask, 'CHANGE'] / df_clean.loc[mask, 'PREV_CLOSE']) * 100
        df_clean.loc[~mask, 'CHANGE_PERCENT'] = 0
        
        # 計算成交額（百萬）- 如果 VALUE 存在
        if 'VALUE' in df_clean.columns:
            df_clean['VALUE_MILLIONS'] = df_clean['VALUE'] / 1_000_000
        else:
            df_clean['VALUE_MILLIONS'] = 0
        
        print(f"✅ 清洗完成，有效數據: {len(df_clean)} 行")
        return df_clean
    
    def filter_stocks(self, df):
        """过滤股票"""
        print(f"🔍 应用过滤条件 (股价 >= SGD {self.threshold})...")
        
        if len(df) == 0:
            return df
        
        initial_count = len(df)
        df_filtered = df.copy()
        
        # 1. 去除停牌股票
        if 'IS_SUSPENDED' in df_filtered.columns:
            susp_mask = ~df_filtered['IS_SUSPENDED']
            df_filtered = df_filtered[susp_mask].copy()
            self.stats['suspended_removed'] = initial_count - len(df_filtered)
            print(f"   - 去除停牌股: {self.stats['suspended_removed']} 支")
        
        # 2. 去除 Penny Stocks
        if len(df_filtered) > 0:
            penny_mask = df_filtered['LAST'] >= self.threshold
            df_filtered = df_filtered[penny_mask].copy()
            self.stats['penny_removed'] = len(df_filtered[~penny_mask]) if len(df_filtered) > 0 else 0
            print(f"   - 去除Penny Stocks (股价<{self.threshold}): {self.stats['penny_removed']} 支")
        
        # 3. 去除低成交量股票
        if len(df_filtered) > 0 and 'VOLUME' in df_filtered.columns:
            volume_mask = df_filtered['VOLUME'] >= self.min_volume
            df_filtered = df_filtered[volume_mask].copy()
            self.stats['low_volume_removed'] = len(df_filtered[~volume_mask]) if len(df_filtered) > 0 else 0
            print(f"   - 去除低成交量 (<{self.min_volume}股): {self.stats['low_volume_removed']} 支")
        
        self.stats['final'] = len(df_filtered)
        
        print(f"✅ 过滤完成: {self.stats['final']} 支股票 (从 {initial_count} 支中筛选)")
        return df_filtered
    
    def calculate_ai_scores(self, df):
        """计算AI选股评分"""
        print("🤖 计算AI选股评分...")
        
        if len(df) == 0:
            print("⚠️ 沒有股票可評分")
            return df
        
        df_scored = df.copy()
        
        # 1. 漲跌幅評分 (最高30分)
        df_scored['SCORE_CHANGE'] = df_scored['CHANGE_PERCENT'].clip(-10, 15).apply(
            lambda x: min(30, max(0, (x + 2) * 2.5)) if x > 0 else max(0, (x + 5) * 1.5)
        )
        
        # 2. 成交量評分 (最高25分)
        if len(df_scored) > 0 and 'VOLUME' in df_scored.columns:
            median_volume = df_scored['VOLUME'].median()
            if median_volume > 0:
                df_scored['VOLUME_RATIO'] = df_scored['VOLUME'] / median_volume
            else:
                df_scored['VOLUME_RATIO'] = 1
            df_scored['SCORE_VOLUME'] = df_scored['VOLUME_RATIO'].clip(0, 5).apply(lambda x: min(25, x * 5))
        else:
            df_scored['SCORE_VOLUME'] = 0
        
        # 3. 價格位置評分 (最高20分)
        price_range = df_scored['HIGH'] - df_scored['LOW']
        price_range = price_range.replace(0, 0.001)  # 避免除零
        df_scored['PRICE_POSITION'] = (df_scored['LAST'] - df_scored['LOW']) / price_range
        df_scored['PRICE_POSITION'] = df_scored['PRICE_POSITION'].clip(0, 1)
        
        def score_position(x):
            if x > 0.8:
                return 20
            elif x > 0.6:
                return 15
            elif x > 0.4:
                return 10
            elif x > 0.2:
                return 5
            else:
                return 2
        df_scored['SCORE_POSITION'] = df_scored['PRICE_POSITION'].apply(score_position)
        
        # 4. 成交額評分 (最高15分)
        if len(df_scored) > 0 and 'VALUE_MILLIONS' in df_scored.columns:
            max_value = df_scored['VALUE_MILLIONS'].max()
            if max_value > 0:
                df_scored['SCORE_VALUE'] = (df_scored['VALUE_MILLIONS'] / max_value * 15).clip(0, 15)
            else:
                df_scored['SCORE_VALUE'] = 0
        else:
            df_scored['SCORE_VALUE'] = 0
        
        # 5. 板塊評分 (最高10分)
        def score_market(market):
            market_str = str(market).upper()
            if 'MAINBOARD' in market_str:
                return 10
            elif 'CATALIST' in market_str:
                return 7
            else:
                return 5
        df_scored['SCORE_MARKET'] = df_scored['MARKET'].apply(score_market)
        
        # 總評分
        df_scored['TOTAL_SCORE'] = (
            df_scored['SCORE_CHANGE'] + 
            df_scored['SCORE_VOLUME'] + 
            df_scored['SCORE_POSITION'] + 
            df_scored['SCORE_VALUE'] + 
            df_scored['SCORE_MARKET']
        )
        
        # 生成推薦
        def get_recommendation(score):
            if score >= 80:
                return '强烈买入'
            elif score >= 65:
                return '买入'
            elif score >= 50:
                return '关注'
            elif score >= 35:
                return '持有'
            else:
                return '观察'
        
        df_scored['RECOMMENDATION'] = df_scored['TOTAL_SCORE'].apply(get_recommendation)
        
        print(f"✅ 评分完成，最高分: {df_scored['TOTAL_SCORE'].max():.1f}")
        return df_scored
    
    def generate_picks(self, df, top_n=10):
        """生成AI选股推荐列表 - 只取前10支"""
        if len(df) == 0:
            return []
        
        # 按總評分排序
        df_sorted = df.sort_values('TOTAL_SCORE', ascending=False)
        
        # 只取前10支股票
        top_picks = df_sorted.head(top_n)
        
        picks = []
        for _, row in top_picks.iterrows():
            # 獲取板塊名稱
            market = str(row['MARKET']).strip()
            if 'MAINBOARD' in market.upper():
                sector = '主板'
            elif 'CATALIST' in market.upper():
                sector = '凱利板'
            else:
                sector = market
            
            pick = {
                'code': str(row['STOCK_CODE']).strip(),
                'name': str(row['NAME']).strip(),
                'current_price': round(row['LAST'], 3),
                'price': round(row['LAST'], 3),
                'change': round(row['CHANGE'], 3) if pd.notna(row['CHANGE']) else 0,
                'change_percent': round(row['CHANGE_PERCENT'], 2) if pd.notna(row['CHANGE_PERCENT']) else 0,
                'volume': int(row['VOLUME']) if pd.notna(row['VOLUME']) else 0,
                'value_millions': round(row['VALUE_MILLIONS'], 2) if pd.notna(row['VALUE_MILLIONS']) else 0,
                'market': market,
                'sector': sector,
                'sector_name': sector,
                'score': round(row['TOTAL_SCORE'], 1),
                'recommendation': row['RECOMMENDATION']
            }
            picks.append(pick)
        
        return picks
    
    def process_file(self, input_file, output_dir='.', top_n=10):
        """处理单个文件的主流程 - 只輸出前10支股票"""
        print(f"\n🚀 开始处理: {os.path.basename(input_file)}")
        
        # 解析日期 - 從文件名提取
        filename = os.path.basename(input_file)
        import re
        date_match = re.search(r'(\d{8})', filename)
        if date_match:
            date_str = date_match.group(1)
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        
        print(f"📅 日期: {date_str}")
        
        # 讀取數據
        df = self.parse_sgx_dat(input_file)
        if df is None or len(df) == 0:
            print("❌ 無法讀取數據")
            return None
        
        # 清洗數據
        df = self.clean_data(df)
        
        if len(df) == 0:
            print("⚠️ 清洗後沒有股票")
            return None
        
        # 過濾股票
        df = self.filter_stocks(df)
        
        if len(df) == 0:
            print("⚠️ 過濾後沒有股票")
            return None
        
        # 計算AI評分
        df = self.calculate_ai_scores(df)
        
        # 生成推薦 - 只取前10支
        picks = self.generate_picks(df, top_n)
        
        # 準備輸出數據 - 包含完整統計但只輸出前10支推薦
        output_data = {
            'date': date_str,
            'date_id': date_str,
            'date_display': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
            'total_stocks': len(df),           # 過濾後的總股票數
            'picks': picks,                      # 只包含前10支推薦
            'stats': self.stats,
            'generated_at': datetime.now().isoformat()
        }
        
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存最新數據 - 給 AI選股 頁面用 (只包含前10支)
        latest_file = os.path.join(output_dir, 'sgx_picks_latest.json')
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"💾 保存最新數據 (前{top_n}支): {latest_file}")
        
        # 保存歷史數據 - 完整數據 (所有過濾後的股票)
        history_dir = os.path.join(output_dir, 'history')
        os.makedirs(history_dir, exist_ok=True)
        
        # 歷史數據要保存完整列表 (所有過濾後的股票)
        history_picks = []
        df_sorted = df.sort_values('TOTAL_SCORE', ascending=False)
        for _, row in df_sorted.iterrows():
            market = str(row['MARKET']).strip()
            if 'MAINBOARD' in market.upper():
                sector = '主板'
            elif 'CATALIST' in market.upper():
                sector = '凱利板'
            else:
                sector = market
            
            history_picks.append({
                'code': str(row['STOCK_CODE']).strip(),
                'name': str(row['NAME']).strip(),
                'current_price': round(row['LAST'], 3),
                'price': round(row['LAST'], 3),
                'change': round(row['CHANGE'], 3) if pd.notna(row['CHANGE']) else 0,
                'change_percent': round(row['CHANGE_PERCENT'], 2) if pd.notna(row['CHANGE_PERCENT']) else 0,
                'volume': int(row['VOLUME']) if pd.notna(row['VOLUME']) else 0,
                'value_millions': round(row['VALUE_MILLIONS'], 2) if pd.notna(row['VALUE_MILLIONS']) else 0,
                'market': market,
                'sector': sector,
                'sector_name': sector,
                'score': round(row['TOTAL_SCORE'], 1),
                'recommendation': row['RECOMMENDATION']
            })
        
        history_data = {
            'date': date_str,
            'date_id': date_str,
            'date_display': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
            'total_stocks': len(history_picks),  # 所有過濾後的股票
            'picks': history_picks,                # 完整列表
            'stats': self.stats,
            'generated_at': datetime.now().isoformat()
        }
        
        history_file = os.path.join(history_dir, f'sgx_picks_{date_str}.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        print(f"💾 保存歷史數據 (完整{len(history_picks)}支): {history_file}")
        
        # 更新日期配置
        self.update_date_config(output_dir, date_str, f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
        
        print(f"✅ 處理完成! AI推薦 {len(picks)} 支股票 (前{top_n}名)")
        print(f"📊 統計: 總股票 {self.stats['total']} -> 過濾後 {self.stats['final']}")
        print(f"   - 停牌: {self.stats['suspended_removed']}")
        print(f"   - Penny: {self.stats['penny_removed']}")
        print(f"   - 低量: {self.stats['low_volume_removed']}")
        
        return output_data
    
    def update_date_config(self, output_dir, date_id, date_display):
        """更新日期配置文件"""
        config_file = os.path.join(output_dir, 'sgx_date_config.js')
        
        # 讀取現有配置
        existing_dates = []
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    match = re.search(r'window\.availableDates\s*=\s*(\[.*?\]);', content, re.DOTALL)
                    if match:
                        import ast
                        existing_dates = ast.literal_eval(match.group(1))
                    else:
                        existing_dates = []
            except Exception as e:
                print(f"⚠️ 讀取日期配置失敗: {e}")
                existing_dates = []
        
        # 添加新日期（如果不存在）
        new_date = {'id': date_id, 'display': date_display}
        exists = False
        for d in existing_dates:
            if d.get('id') == date_id:
                exists = True
                break
        
        if not exists:
            existing_dates.append(new_date)
        
        # 按日期排序（最新的在前）
        existing_dates.sort(key=lambda x: x['id'], reverse=True)
        
        # 只保留最近30天的日期，避免檔案太大
        if len(existing_dates) > 30:
            existing_dates = existing_dates[:30]
        
        # 寫入文件
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write('// SGX日期配置文件\n')
            f.write('// 自動生成，請勿手動編輯\n')
            f.write('window.availableDates = ')
            json.dump(existing_dates, f, indent=2, ensure_ascii=False)
            f.write(';\n')
        
        print(f"📅 更新日期配置: {config_file} (共 {len(existing_dates)} 天)")

def main():
    parser = argparse.ArgumentParser(description='SGX EOD數據處理工具 - 輸出前10支股票')
    parser.add_argument('input', help='輸入文件或目錄')
    parser.add_argument('--output', '-o', default='.', help='輸出目錄 (默認: 當前目錄)')
    parser.add_argument('--threshold', '-t', type=float, default=PENNY_THRESHOLD, help=f'Penny Stock閾值 (默認: {PENNY_THRESHOLD})')
    parser.add_argument('--min-volume', '-v', type=int, default=MIN_VOLUME, help=f'最小成交量 (默認: {MIN_VOLUME})')
    parser.add_argument('--top', '-n', type=int, default=TOP_N, help=f'推薦股票數量 (默認: {TOP_N})')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📈 SGX EOD 數據處理器 - 前10推薦版")
    print("=" * 60)
    print(f"輸入: {args.input}")
    print(f"輸出: {args.output}")
    print(f"閾值: SGD {args.threshold}")
    print(f"最小成交量: {args.min_volume} 股")
    print(f"推薦數量: {args.top} (只輸出前{args.top}名)")
    print("-" * 60)
    
    # 創建處理器
    processor = SGXEODProcessor(threshold=args.threshold, min_volume=args.min_volume)
    
    # 處理輸入
    if os.path.isfile(args.input):
        # 處理單個文件
        processor.process_file(args.input, args.output, args.top)
    elif os.path.isdir(args.input):
        # 處理目錄下所有.dat文件
        dat_files = glob.glob(os.path.join(args.input, '*.dat'))
        dat_files.extend(glob.glob(os.path.join(args.input, '*.DAT')))
        print(f"📁 找到 {len(dat_files)} 個.dat文件")
        
        # 按文件名排序，取最新的5個
        for dat_file in sorted(dat_files)[-5:]:
            processor.process_file(dat_file, args.output, args.top)
    else:
        print(f"❌ 無效路徑: {args.input}")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ 所有處理完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()