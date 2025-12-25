#!/usr/bin/env python3
"""
======================================================================
🚀 Bursa Malaysia AI選股神器 - 完整生產版 (安全JSON版本)
整合了CSV規範化功能
======================================================================
🎯 功能:
  1. ✅ CSV數據規範化（兼容多種格式）
  2. ✅ 生成 latest_price.json (web目錄) - 安全JSON格式
  3. ✅ 生成 picks_latest.json (web目錄) - 安全JSON格式
  4. ✅ 生成 picks_YYYYMMDD.json (web/history目錄)
  5. ✅ 自動備份到scripts目錄
  6. ✅ 自動清理30天前舊文件
  7. ✅ 完全處理NaN值，確保JSON有效性
======================================================================
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import shutil
import csv
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 获取当前脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 输出目录配置
WEB_DIR = os.path.join(BASE_DIR, "web")
HISTORY_DIR = os.path.join(WEB_DIR, "history")
DATA_DIR = os.path.join(SCRIPT_DIR, "data", "bursa", "picks")
BACKUP_DIR = os.path.join(SCRIPT_DIR, "backups")

# 配置目录
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
EOD_CONFIG_PATH = os.path.join(CONFIG_DIR, "eod_config.json")

# 确保所有目录存在
for directory in [WEB_DIR, HISTORY_DIR, DATA_DIR, BACKUP_DIR, CONFIG_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# CSV规范化功能（整合自 normalize_eod.py）
# ============================================================================

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"⚠️  配置文件不存在: {config_path}")
        print("✅ 创建默认配置...")
        default_config = {
            "schema": ["code", "name", "last_price", "change", "change_percent", 
                      "volume", "sector", "open", "high", "low", "last_updated"],
            "map": {
                "股票代码": "code",
                "股票名称": "name",
                "最新价": "last_price",
                "涨跌": "change",
                "涨跌幅": "change_percent",
                "成交量": "volume",
                "行业": "sector",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "更新时间": "last_updated"
            },
            "fill": {
                "sector": "Unknown",
                "last_updated": "15:30:22"
            },
            "sector_lookup": {
                "1": "工业与消费产品",
                "2": "金融",
                "3": "房地产",
                "4": "科技",
                "5": "能源",
                "6": "医疗",
                "7": "运输与物流",
                "8": "建筑",
                "9": "种植",
                "10": "服务"
            }
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_delimiter(path):
    """检测CSV文件的分隔符"""
    with open(path, "r", newline="", encoding="utf-8") as f:
        sample = f.read(4096)
    
    # 统计制表符和逗号的出现次数
    tab_count = sample.count("\t")
    comma_count = sample.count(",")
    
    # 如果制表符多于逗号，则使用制表符
    if tab_count > comma_count and tab_count >= 5:  # 至少5个制表符
        return "\t"
    return ","

def normalize_header(header, aliases):
    """规范化列名"""
    normalized = []
    for col in header:
        c = col.strip()
        # 尝试多种可能的列名格式
        if c in aliases:
            normalized.append(aliases[c])
        else:
            # 检查是否包含关键字段
            if any(keyword in c.lower() for keyword in ["code", "股票代码", "stock"]):
                normalized.append("code")
            elif any(keyword in c.lower() for keyword in ["name", "股票名称", "stock name"]):
                normalized.append("name")
            elif any(keyword in c.lower() for keyword in ["price", "最新价", "last"]):
                normalized.append("last_price")
            elif any(keyword in c.lower() for keyword in ["change", "涨跌", "涨跌幅"]):
                normalized.append("change_percent")
            elif any(keyword in c.lower() for keyword in ["volume", "成交量"]):
                normalized.append("volume")
            elif any(keyword in c.lower() for keyword in ["sector", "行业"]):
                normalized.append("sector")
            else:
                normalized.append(c)
    return normalized

def normalize_csv_file(input_path, output_path=None, config_path=None):
    """
    规范化CSV文件
    返回规范化后的DataFrame和输出路径
    """
    # ... 前面的代碼不變 ...
    
    # 創建新的DataFrame
    normalized_data = {}
    
    for orig_col, norm_col in column_mapping.items():
        if orig_col in df.columns:
            normalized_data[norm_col] = df[orig_col]
            print(f"  ✅ 映射 {orig_col} → {norm_col}")
        else:
            print(f"  ⚠️  列不存在: {orig_col}")
    
    # 創建新的DataFrame
    normalized_df = pd.DataFrame(normalized_data)
    
    # ========== 清理代碼列 ==========
    if 'code' in normalized_df.columns:
        print("  🔧 清理股票代碼格式...")
        def clean_stock_code(code):
            if isinstance(code, str):
                # 移除 Excel 公式格式 ="2429"
                code = code.strip()
                if code.startswith('="') and code.endswith('"'):
                    code = code[2:-1]  # 移除 =" 和 "
                elif code.startswith('='):
                    code = code[1:]  # 移除 =
                # 移除所有非數字字符（保留字母，因為權證可能有字母）
                # 只移除空格、引號、等號等不需要的字符
                import re
                code = re.sub(r'[=\s"\']', '', code)
                # 補齊前導零（如果需要）
                if code.isdigit():
                    code = code.zfill(4)  # 補齊到4位數字
            return code
        
        normalized_df['code'] = normalized_df['code'].apply(clean_stock_code)
        print("  ✅ 股票代碼清理完成")

    if config_path is None:
        config_path = EOD_CONFIG_PATH
    
    config = load_config(config_path)
    schema = config["schema"]
    aliases = config.get("map", {})
    defaults = config.get("fill", {})
    sector_lookup = config.get("sector_lookup", {})
    
    print(f"  📁 输入文件: {input_path}")
    
    try:
        # 直接读取CSV
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"  ❌ 无法读取CSV文件: {e}")
        return None, None
    
    print(f"  📈 读取 {len(df)} 行数据")
    print(f"  📋 原始列名: {list(df.columns)}")
    
    # 清理列名：去除空格
    df.columns = [col.strip() for col in df.columns]
    
    # ========== 修复列名映射问题 ==========
    # 直接的手动映射，避免自动映射出错
    column_mapping = {
        'Code': 'code',
        'Stock': 'name',           # 修复：Stock应该是name，不是code
        'Sector': 'sector',        # 原始行业列
        'Sector_Code': 'sector_code',  # 修复：避免重复的code
        'Sector_Name': 'sector_name',  # 修复：避免重复的name
        'Last': 'last_price',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Prv Close': 'prev_close',
        'Chg%': 'change_percent',
        'Vol': 'volume'
    }
    
    # 创建新的DataFrame
    normalized_data = {}
    
    for orig_col, norm_col in column_mapping.items():
        if orig_col in df.columns:
            normalized_data[norm_col] = df[orig_col]
            print(f"  ✅ 映射 {orig_col} → {norm_col}")
        else:
            print(f"  ⚠️  列不存在: {orig_col}")
    
    # 创建新的DataFrame
    normalized_df = pd.DataFrame(normalized_data)
    
    # 如果sector_name不存在，但sector存在，使用sector
    if 'sector_name' not in normalized_df.columns and 'sector' in normalized_df.columns:
        normalized_df['sector_name'] = normalized_df['sector']
    
    # 确保必要的列存在
    required_columns = ['code', 'name', 'last_price', 'change_percent', 
                       'volume', 'sector_name', 'open', 'high', 'low']
    
    for col in required_columns:
        if col not in normalized_df.columns:
            if col == 'change_percent':
                # 尝试从Chg%计算
                if 'change_percent' not in normalized_df.columns and 'last_price' in normalized_df.columns and 'prev_close' in normalized_df.columns:
                    try:
                        normalized_df['change_percent'] = ((normalized_df['last_price'] - normalized_df['prev_close']) / 
                                                          normalized_df['prev_close'] * 100)
                    except:
                        normalized_df['change_percent'] = 0.0
                else:
                    normalized_df['change_percent'] = 0.0
            elif col in defaults:
                normalized_df[col] = defaults[col]
            else:
                normalized_df[col] = None
    
    # 添加最后更新时间
    normalized_df['last_updated'] = datetime.now().strftime('%H:%M:%S')
    
    # 转换数值列
    numeric_columns = ["last_price", "open", "high", "low", "volume", "change_percent"]
    for col in numeric_columns:
        if col in normalized_df.columns:
            try:
                normalized_df[col] = pd.to_numeric(normalized_df[col], errors="coerce")
            except:
                normalized_df[col] = None
    
    # 生成输出路径
    if output_path is None:
        input_name = os.path.basename(input_path)
        name_without_ext = os.path.splitext(input_name)[0]
        output_name = f"{name_without_ext}_normalized.csv"
        output_path = os.path.join(os.path.dirname(input_path), output_name)
    
    # 保存规范化后的CSV
    normalized_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"  💾 保存规范化文件: {output_path}")
    print(f"  📋 最终列: {list(normalized_df.columns)}")
    print(f"  📊 数据行数: {len(normalized_df)}")
    
    return normalized_df, output_path

# ============================================================================
# AI選股核心功能
# ============================================================================

def standardize_columns(df):
    """標準化列名"""
    column_mapping = {
        '股票代碼': 'code',
        '股票名稱': 'name',
        '收盤價': 'last_price',
        '開盤價': 'open',
        '最高價': 'high',
        '最低價': 'low',
        '成交量': 'volume',
        '漲跌': 'change',
        '漲跌幅': 'change_percent',
        '板塊': 'sector',
        '更新時間': 'last_updated'
    }
    
    df = df.rename(columns=column_mapping)
    
    # 確保所有必需的列都存在
    required_columns = ['code', 'name', 'last_price', 'open', 'high', 'low', 
                       'volume', 'change', 'change_percent', 'sector']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    return df

def normalize_dataframe(df):
    """標準化數據框：重命名列並轉換數據類型"""
    print("  🔧 標準化數據...")
    
    # 創建副本以避免修改原始數據
    df_norm = df.copy()
    
    # 標準化列名
    df_norm = standardize_columns(df_norm)
    
    # 嘗試轉換數值列
    numeric_columns = ['last_price', 'open', 'high', 'low', 'volume', 'change', 'change_percent']
    
    for col in numeric_columns:
        if col in df_norm.columns:
            try:
                # 首先確保是 Series 對象
                if isinstance(df_norm[col], pd.Series):
                    df_norm[col] = pd.to_numeric(df_norm[col], errors='coerce')
                else:
                    # 如果不是 Series，轉換為 Series
                    df_norm[col] = pd.to_numeric(pd.Series(df_norm[col]), errors='coerce')
                    print(f"    ⚠️  列 '{col}' 已強制轉換為 Series")
            except Exception as e:
                print(f"    ❌ 無法轉換列 '{col}': {e}")
                # 如果轉換失敗，保持原樣
                continue
    
    print("  ✅ 標準化完成")
    return df_norm

def calculate_technical_indicators(df):
    """計算技術指標"""
    print("  📊 計算技術指標...")
    
    df_tech = df.copy()
    
    # 確保有必要的列
    if 'last_price' not in df_tech.columns:
        print("    ⚠️  缺少 'last_price' 列，跳過技術指標計算")
        return df_tech
    
    # 計算簡單技術指標
    try:
        # RSI (相對強弱指數) - 簡化版本
        price_series = df_tech['last_price'].astype(float)
        
        # 計算價格變化
        delta = price_series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 計算平均增益和平均損失
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        
        # 計算RS
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df_tech['rsi'] = 100 - (100 / (1 + rs))
        
        # 簡單移動平均線
        df_tech['sma_5'] = price_series.rolling(window=5, min_periods=1).mean()
        df_tech['sma_10'] = price_series.rolling(window=10, min_periods=1).mean()
        
        # 價格動量
        df_tech['momentum'] = price_series.pct_change(periods=5) * 100
        
        print("  ✅ 技術指標計算完成")
        
    except Exception as e:
        print(f"    ⚠️  技術指標計算錯誤: {e}")
    
    return df_tech

def ai_scoring(df):
    """AI評分系統"""
    print("  🧠 AI評分系統啟動...")
    
    scores = []
    
    for idx, row in df.iterrows():
        score = 50  # 基礎分
        
        try:
            # 價格相關評分
            if 'change_percent' in row and pd.notna(row['change_percent']):
                change = float(row['change_percent'])
                if change > 5:
                    score += 15
                elif change > 2:
                    score += 10
                elif change > 0:
                    score += 5
                elif change < -5:
                    score -= 10
                elif change < 0:
                    score -= 5
            
            # 成交量評分
            if 'volume' in row and pd.notna(row['volume']):
                volume = float(row['volume'])
                # 簡單的成交量評分
                if volume > 1000000:
                    score += 10
                elif volume > 100000:
                    score += 5
                elif volume < 10000:
                    score -= 5
            
            # RSI評分
            if 'rsi' in row and pd.notna(row['rsi']):
                rsi = float(row['rsi'])
                if 30 < rsi < 70:
                    score += 5
                elif rsi < 30:
                    score += 10  # 超賣，可能反彈
                elif rsi > 70:
                    score -= 5   # 超買
            
            # 移動平均線評分
            if 'last_price' in row and 'sma_5' in row and pd.notna(row['last_price']) and pd.notna(row['sma_5']):
                price = float(row['last_price'])
                sma5 = float(row['sma_5'])
                if price > sma5:
                    score += 5
            
            # 確保分數在合理範圍
            score = max(0, min(100, score))
            
        except Exception as e:
            print(f"    ⚠️  股票 {row.get('code', 'N/A')} 評分錯誤: {e}")
            score = 50
        
        scores.append(score)
    
    df = df.copy()
    df['score'] = scores
    df['score'] = df['score'].round(1)
    
    print("  ✅ AI評分完成")
    return df

def generate_recommendation(row):
    """生成投資建議"""
    score = row.get('score', 50)
    change = row.get('change_percent', 0)
    rsi = row.get('rsi', 50)
    
    if score >= 80:
        return "👍強力買入", "高潛力", "低"
    elif score >= 70:
        return "👍買入", "中高潛力", "中低"
    elif score >= 60:
        return "🤔考慮買入", "中等潛力", "中"
    elif score >= 50:
        return "⚖️中性", "觀望", "中高"
    elif score >= 40:
        return "⚠️考慮賣出", "風險偏高", "高"
    else:
        return "🚫賣出", "高風險", "很高"

def calculate_potential_score(row):
    """計算潛力分數"""
    score = row.get('score', 50)
    change = row.get('change_percent', 0)
    
    # 基礎潛力分數
    potential = score
    
    # 根據漲跌幅調整
    if change > 5:
        potential += 10
    elif change > 2:
        potential += 5
    elif change < -5:
        potential -= 5
    
    # 根據成交量調整
    volume = row.get('volume', 0)
    if volume > 500000:
        potential += 5
    
    # 限制範圍
    potential = max(0, min(100, potential))
    
    return round(potential)

def generate_potential_reasons(row):
    """生成潛力原因"""
    reasons = []
    
    if row.get('change_percent', 0) > 2:
        reasons.append("價格趨勢向上")
    
    if row.get('volume', 0) > 100000:
        reasons.append("成交量活躍")
    
    if row.get('score', 50) > 70:
        reasons.append("AI評分高")
    
    if 'rsi' in row and row['rsi'] < 40:
        reasons.append("RSI顯示可能超賣反彈")
    elif 'rsi' in row and row['rsi'] > 60:
        reasons.append("RSI顯示強勢")
    
    if len(reasons) == 0:
        reasons.append("綜合評估中性")
    
    return "，".join(reasons[:3])

def generate_stock_picks(df, max_picks=20):
    """生成AI選股清單"""
    print("  🎯 生成AI選股清單...")
    
    # 複製數據
    df_picks = df.copy()
    
    # 計算額外指標
    df_picks['potential_score'] = df_picks.apply(calculate_potential_score, axis=1)
    
    # 生成建議
    recommendations = df_picks.apply(generate_recommendation, axis=1)
    df_picks['recommendation'] = recommendations.apply(lambda x: x[0])
    df_picks['risk_level'] = recommendations.apply(lambda x: x[2])
    df_picks['status'] = recommendations.apply(lambda x: x[1])
    
    # 生成潛力原因
    df_picks['potential_reasons'] = df_picks.apply(generate_potential_reasons, axis=1)
    
    # 添加樂器類型檢測（簡單版本）
    def detect_instrument_type(code):
        if isinstance(code, str):
            if '-' in code or code.endswith(('WA', 'WB', 'WC', 'WR')):
                return "Warrant"
            elif len(code) >= 5 and code[-1].isalpha():
                return "Preference"
        return "Stock"
    
    df_picks['instrument_type'] = df_picks['code'].apply(detect_instrument_type)
    
    # 按潛力分數排序
    df_picks = df_picks.sort_values('potential_score', ascending=False)
    
    # 限制數量
    df_picks = df_picks.head(max_picks)
    
    # 添加排名
    df_picks['rank'] = range(1, len(df_picks) + 1)
    
    # 重新排列列
    pick_columns = ['rank', 'code', 'name', 'instrument_type', 'sector',
                   'current_price', 'daily_change', 'score', 'potential_score',
                   'potential_reasons', 'recommendation', 'risk_level',
                   'rsi', 'volume', 'status']
    
    # 確保所有列都存在
    for col in pick_columns:
        if col not in df_picks.columns:
            if col == 'current_price':
                df_picks[col] = df_picks.get('last_price', 0)
            elif col == 'daily_change':
                df_picks[col] = df_picks.get('change_percent', 0)
            else:
                df_picks[col] = None
    
    df_picks = df_picks[pick_columns]
    
    print(f"  ✅ 生成 {len(df_picks)} 個選股")
    return df_picks

def save_safe_json(data, filepath, indent=2):
    """安全保存JSON文件，處理NaN值"""
    def safe_serializer(obj):
        if isinstance(obj, (np.float32, np.float64)):
            if np.isnan(obj):
                return None
            return float(obj)
        if isinstance(obj, (np.int32, np.int64, np.int8)):
            return int(obj)
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        if pd.isna(obj):
            return None
        raise TypeError(f"無法序列化類型: {type(obj)}")

# 確保代碼是字符串
    def ensure_string_codes(obj):
        if isinstance(obj, dict):
            return {k: ensure_string_codes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ensure_string_codes(item) for item in obj]
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            # 檢查是否是代碼字段
            if isinstance(obj, int) and 1000 <= obj <= 9999:
                return str(obj).zfill(4)
            return obj
        else:
            return obj
    
    try:
        # 清理數據
        cleaned_data = ensure_string_codes(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=indent, default=safe_serializer, ensure_ascii=False)
        print(f"  💾 保存JSON文件: {filepath}")
        return True
    except Exception as e:
        print(f"  ❌ 保存JSON失敗 {filepath}: {e}")
        return False
```
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=safe_serializer, ensure_ascii=False)
        print(f"  💾 保存JSON文件: {filepath}")
        return True
    except Exception as e:
        print(f"  ❌ 保存JSON失敗 {filepath}: {e}")
        return False

def create_latest_price_json(df, output_dir):
    """創建latest_price.json"""
    print("  📄 創建 latest_price.json...")
    
    # 準備數據
    stocks_list = []
    
    for idx, row in df.iterrows():
        stock_data = {
            'code': str(row.get('code', '')),
            'name': str(row.get('name', '')),
            'last_price': float(row.get('last_price', 0)) if pd.notna(row.get('last_price')) else 0,
            'change': float(row.get('change', 0)) if pd.notna(row.get('change')) else 0,
            'change_percent': float(row.get('change_percent', 0)) if pd.notna(row.get('change_percent')) else 0,
            'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
            'sector': str(row.get('sector', 'Unknown')),
            'open': float(row.get('open', 0)) if pd.notna(row.get('open')) else 0,
            'high': float(row.get('high', 0)) if pd.notna(row.get('high')) else 0,
            'low': float(row.get('low', 0)) if pd.notna(row.get('low')) else 0,
            'last_updated': str(row.get('last_updated', '15:30:22'))
        }
        stocks_list.append(stock_data)
    
    data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_date': datetime.now().strftime('%Y-%m-%d'),
        'total_stocks': len(stocks_list),
        'market': 'Bursa Malaysia',
        'stocks': stocks_list
    }
    
    filepath = os.path.join(output_dir, 'latest_price.json')
    if save_safe_json(data, filepath):
        return filepath
    return None

def create_picks_json(df_picks, output_dir, date_str=None):
    """創建選股JSON文件"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')
    
    print(f"  📄 創建 picks_{date_str}.json...")
    
    # 準備數據
    picks_list = []
    
    for idx, row in df_picks.iterrows():
        pick_data = {
            'rank': int(row.get('rank', 0)),
            'code': str(row.get('code', '')),
            'name': str(row.get('name', '')),
            'instrument_type': str(row.get('instrument_type', 'Stock')),
            'sector': str(row.get('sector', '')),
            'current_price': float(row.get('current_price', 0)) if pd.notna(row.get('current_price')) else 0,
            'daily_change': float(row.get('daily_change', 0)) if pd.notna(row.get('daily_change')) else 0,
            'score': float(row.get('score', 0)) if pd.notna(row.get('score')) else 0,
            'potential_score': int(row.get('potential_score', 0)) if pd.notna(row.get('potential_score')) else 0,
            'potential_reasons': str(row.get('potential_reasons', '')),
            'recommendation': str(row.get('recommendation', '')),
            'risk_level': str(row.get('risk_level', '')),
            'rsi': float(row.get('rsi', 0)) if pd.notna(row.get('rsi')) else 0,
            'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
            'status': str(row.get('status', ''))
        }
        picks_list.append(pick_data)
    
    data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'picks': picks_list
    }
    
    filepath = os.path.join(output_dir, f'picks_{date_str}.json')
    if save_safe_json(data, filepath):
        return filepath
    return None

def backup_files(source_dir, backup_dir, prefix="backup_"):
    """備份文件"""
    print("  💾 創建備份...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"{prefix}{timestamp}")
    
    os.makedirs(backup_path, exist_ok=True)
    
    # 備份文件
    files_to_backup = ['latest_price.json', 'picks_latest.json']
    
    for filename in files_to_backup:
        source_file = os.path.join(source_dir, filename)
        if os.path.exists(source_file):
            shutil.copy2(source_file, os.path.join(backup_path, filename))
            print(f"    ✅ 備份 {filename}")
    
    return backup_path

def cleanup_old_files(directory, days=30):
    """清理舊文件"""
    print(f"  🗑️  清理{days}天前舊文件...")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for filename in os.listdir(directory):
        if filename.startswith('picks_') and filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            
            # 檢查文件修改時間
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mod_time < cutoff_date:
                os.remove(filepath)
                deleted_count += 1
                print(f"    🗑️  刪除舊文件: {filename}")
    
    if deleted_count > 0:
        print(f"  ✅ 刪除 {deleted_count} 個舊文件")
    else:
        print("  ✅ 無需清理")

def main():
    """主函數"""
    print("="*70)
    print("🚀 Bursa Malaysia AI選股神器 - 完整生產版 (整合CSV規範化)")
    print("="*70)
    print("🎯 功能:")
    print("  1. ✅ CSV數據規範化（兼容多種格式）")
    print("  2. ✅ 生成 latest_price.json (web目錄) - 安全JSON格式")
    print("  3. ✅ 生成 picks_latest.json (web目錄) - 安全JSON格式")
    print("  4. ✅ 生成 picks_YYYYMMDD.json (web/history目錄)")
    print("  5. ✅ 自動備份到scripts目錄")
    print("  6. ✅ 自動清理30天前舊文件")
    print("  7. ✅ 完全處理NaN值，確保JSON有效性")
    print("="*70)
    
    # 獲取CSV文件路徑
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = input("請輸入CSV文件路徑: ").strip()
    
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        sys.exit(1)
    
    print(f"\n📁 輸入文件: {csv_path}")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print("🔒 安全模式: 已啟用（完全處理NaN值）")
    
    print("\n📁 創建目錄結構...")
    for directory in [WEB_DIR, HISTORY_DIR, DATA_DIR, BACKUP_DIR]:
        print(f"    ✅ 確保目錄存在: {directory}")
    
    # 步驟1: CSV規範化
    print("\n📊 CSV數據規範化...")
    normalized_df, normalized_path = normalize_csv_file(csv_path)
    
    if normalized_df is None:
        print("❌ CSV規範化失敗")
        sys.exit(1)
    
    # 步驟2: 數據標準化
    print("\n🔧 數據處理流程...")
    df_standardized = normalize_dataframe(normalized_df)
    
    # 步驟3: 計算技術指標
    df_technical = calculate_technical_indicators(df_standardized)
    
    # 步驟4: AI評分
    df_scored = ai_scoring(df_technical)
    
    # 步驟5: 生成選股
    df_picks = generate_stock_picks(df_scored, max_picks=20)
    
    # 步驟6: 生成JSON文件
    print("\n💾 生成輸出文件...")
    
    # latest_price.json
    latest_price_file = create_latest_price_json(df_standardized, WEB_DIR)
    
    # picks_latest.json (在web目錄)
    picks_latest_file = create_picks_json(df_picks, WEB_DIR, "latest")
    
    # picks_YYYYMMDD.json (在history目錄)
    date_str = datetime.now().strftime('%Y%m%d')
    picks_history_file = create_picks_json(df_picks, HISTORY_DIR, date_str)
    
    # 備份
    backup_path = backup_files(WEB_DIR, BACKUP_DIR)
    
    # 清理舊文件
    cleanup_old_files(HISTORY_DIR, days=30)
    
    # 總結
    print("\n" + "="*70)
    print("🎉 AI選股完成！")
    print("="*70)
    print(f"📊 輸入數據: {len(df_standardized)} 支股票")
    print(f"🎯 AI選股: {len(df_picks)} 個推薦")
    print(f"💾 生成文件:")
    print(f"   1. {latest_price_file if latest_price_file else 'latest_price.json (失敗)'}")
    print(f"   2. {picks_latest_file if picks_latest_file else 'picks_latest.json (失敗)'}")
    print(f"   3. {picks_history_file if picks_history_file else f'picks_{date_str}.json (失敗)'}")
    print(f"   4. 備份: {backup_path}")
    print(f"\n⏰ 下次運行: python ai_stock_picker_full.py [CSV文件路徑]")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)