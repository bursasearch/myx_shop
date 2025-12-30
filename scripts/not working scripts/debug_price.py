#!/usr/bin/env python3
"""
🔍 偵錯工具 - 找出 latest_price.json 為空的原因
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

def debug_price_issue(csv_file):
    """偵錯價格文件問題"""
    print("=" * 60)
    print("🔍 開始偵錯 latest_price.json 問題")
    print("=" * 60)
    
    # 1. 讀取CSV並檢查結構
    print("📊 1. 讀取CSV文件...")
    df = pd.read_csv(csv_file)
    print(f"   ✅ 讀取 {len(df)} 行, {len(df.columns)} 列")
    
    # 2. 顯示所有列名
    print("\n📋 2. 列名檢查:")
    for i, col in enumerate(df.columns):
        print(f"   [{i:2d}] {col}")
    
    # 3. 檢查關鍵列是否存在
    print("\n🔎 3. 關鍵列檢查:")
    critical_cols = ['Code', 'Stock', 'Last', 'Chg%', 'Vol']
    for col in critical_cols:
        if col in df.columns:
            print(f"   ✅ {col}: 存在")
            # 顯示前幾個值
            sample_vals = df[col].head(3).tolist()
            print(f"       樣本值: {sample_vals}")
        else:
            print(f"   ❌ {col}: 不存在")
    
    # 4. 檢查前幾行數據
    print("\n📝 4. 前5行數據樣本:")
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        code = row.get('Code', 'N/A')
        name = row.get('Stock', 'N/A')
        last_price = row.get('Last', 'N/A')
        chg_pct = row.get('Chg%', 'N/A')
        print(f"   行{i+1}: 代碼={code}, 名稱={name}, 價格={last_price}, 變化={chg_pct}")
    
    # 5. 檢查數據類型
    print("\n🔧 5. 數據類型檢查:")
    for col in ['Code', 'Stock', 'Last', 'Chg%', 'Vol']:
        if col in df.columns:
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            null_count = df[col].isna().sum()
            print(f"   {col}:")
            print(f"     類型: {dtype}")
            print(f"     非空值: {non_null}")
            print(f"     空值: {null_count}")
            
            # 顯示一些樣本值
            if non_null > 0:
                sample = df[col].dropna().head(3).tolist()
                print(f"     樣本: {sample}")
    
    # 6. 測試價格數據提取
    print("\n🧪 6. 測試價格數據提取:")
    test_rows = []
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        try:
            code = str(row.get('Code', '')).strip()
            name = str(row.get('Stock', '')).strip()
            last_price = row.get('Last', 0)
            
            # 清理代碼
            code = code.strip('="')
            
            # 檢查是否有效
            if code and len(code) >= 2 and not pd.isna(last_price) and last_price > 0:
                test_rows.append({
                    'code': code,
                    'name': name,
                    'last_price': float(last_price),
                    'status': '✅ 有效'
                })
            else:
                test_rows.append({
                    'code': code,
                    'name': name,
                    'last_price': last_price,
                    'status': '❌ 無效'
                })
        except Exception as e:
            test_rows.append({
                'code': 'ERROR',
                'name': str(e),
                'last_price': 0,
                'status': '❌ 錯誤'
            })
    
    for i, test in enumerate(test_rows):
        print(f"   行{i+1}: {test['status']} - 代碼={test['code']}, 價格={test['last_price']}")
    
    # 7. 實際生成價格數據測試
    print("\n🚀 7. 實際生成價格數據測試:")
    price_data_list = []
    valid_count = 0
    invalid_reasons = {}
    
    for idx, row in df.iterrows():
        try:
            code_raw = row.get('Code', '')
            if pd.isna(code_raw):
                invalid_reasons['code_na'] = invalid_reasons.get('code_na', 0) + 1
                continue
                
            code = str(code_raw).strip().strip('="')
            if not code or len(code) < 2:
                invalid_reasons['code_invalid'] = invalid_reasons.get('code_invalid', 0) + 1
                continue
            
            last_price = row.get('Last', 0)
            if pd.isna(last_price):
                invalid_reasons['price_na'] = invalid_reasons.get('price_na', 0) + 1
                continue
            
            if last_price <= 0:
                invalid_reasons['price_zero'] = invalid_reasons.get('price_zero', 0) + 1
                continue
            
            # 如果通過所有檢查
            valid_count += 1
            price_data_list.append({
                'code': code,
                'name': str(row.get('Stock', '')).strip(),
                'last_price': float(last_price)
            })
            
            # 顯示前幾個成功的
            if valid_count <= 3:
                print(f"   ✅ 成功 {valid_count}: {code} - 價格: {last_price}")
                
        except Exception as e:
            invalid_reasons['error'] = invalid_reasons.get('error', 0) + 1
    
    print(f"\n📊 8. 統計結果:")
    print(f"   總行數: {len(df)}")
    print(f"   有效數據: {valid_count}")
    print(f"   無效數據原因:")
    for reason, count in invalid_reasons.items():
        print(f"     - {reason}: {count}")
    
    # 9. 生成修復建議
    print("\n💡 9. 修復建議:")
    if valid_count == 0:
        print("   ❌ 問題: 沒有找到任何有效價格數據")
        print("   💡 建議: 檢查以下可能問題:")
        print("     1. 'Last' 列的值可能都是0或NaN")
        print("     2. 'Code' 列可能有格式問題")
        print("     3. 可能需要清理數據")
    else:
        print(f"   ✅ 找到 {valid_count} 個有效價格數據")
        print("   💡 建議: 使用以下代碼修復")
    
    # 10. 生成修復代碼
    print("\n🔧 10. 修復代碼建議:")
    print("""
def fix_price_extraction(df):
    \"\"\"修復價格數據提取\"\"\"
    price_data_list = []
    
    for idx, row in df.iterrows():
        try:
            # 獲取代碼
            code_raw = row.get('Code', '')
            if pd.isna(code_raw):
                continue
            code = str(code_raw).strip().strip('="')
            if not code or len(code) < 2:
                continue
            
            # 獲取價格 - 嘗試多種方式
            last_price = row.get('Last', 0)
            
            # 如果價格是字符串，清理後轉換
            if isinstance(last_price, str):
                last_price = last_price.strip().replace(',', '').replace('%', '')
                try:
                    last_price = float(last_price)
                except:
                    continue
            
            if pd.isna(last_price) or last_price <= 0:
                continue
            
            # 添加到列表
            price_data_list.append({
                'code': code,
                'name': str(row.get('Stock', '')).strip(),
                'last_price': round(float(last_price), 3),
                'change': round(float(row.get('Chg%', 0)), 2)
            })
            
        except Exception:
            continue
    
    return price_data_list
    """)
    
    return valid_count > 0

def main():
    """主函數"""
    print("=" * 60)
    print("🔍 latest_price.json 問題偵錯工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("請輸入CSV文件路徑: ").strip()
    
    if not os.path.exists(csv_file):
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    has_data = debug_price_issue(csv_file)
    
    if has_data:
        print("\n✅ 偵錯完成！應該有數據的！")
        print("💰 可能是提取邏輯有問題！")
    else:
        print("\n⚠️  偵錯完成！可能CSV數據本身有問題！")

if __name__ == "__main__":
    main()
