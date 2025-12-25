#!/usr/bin/env python3
"""
最終版 JSON 修復腳本
修復所有股票代碼格式問題
"""

import os
import json
import sys

def clean_stock_code(code):
    """清理股票代碼"""
    if code is None:
        return ""
    
    code_str = str(code).strip()
    
    # 移除 Excel 公式格式
    if code_str.startswith('="') and code_str.endswith('"'):
        code_str = code_str[2:-1]
    elif code_str.startswith('='):
        code_str = code_str[1:]
    
    # 移除特殊字符
    code_str = code_str.replace('"', '').replace("'", "").replace('=', '')
    
    # 補齊前導零（如果全是數字）
    if code_str.isdigit():
        code_str = code_str.zfill(4)
    
    return code_str

def fix_file(filepath):
    """修復單個文件"""
    print(f"處理: {os.path.basename(filepath)}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # 修復 picks 數據
        if 'picks' in data:
            for item in data['picks']:
                if 'code' in item:
                    old = item['code']
                    new = clean_stock_code(old)
                    if old != new:
                        item['code'] = new
                        modified = True
                        print(f"  🔄 {old} → {new}")
        
        # 修復 stocks 數據
        if 'stocks' in data:
            for item in data['stocks']:
                if 'code' in item:
                    old = item['code']
                    new = clean_stock_code(old)
                    if old != new:
                        item['code'] = new
                        modified = True
                        print(f"  🔄 {old} → {new}")
        
        if modified:
            # 創建備份
            backup = filepath + '.bak'
            import shutil
            shutil.copy2(filepath, backup)
            
            # 保存修復後的文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 已修復（備份: {os.path.basename(backup)}）")
        else:
            print(f"  ✅ 無需修復")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

def main():
    """主函數"""
    print("="*50)
    print("📁 JSON 文件修復工具")
    print("="*50)
    
    # 基礎目錄
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 要修復的文件路徑
    files_to_fix = []
    
    # Web 目錄文件
    web_files = [
        os.path.join(base_dir, 'web', 'picks_latest.json'),
        os.path.join(base_dir, 'web', 'latest_price.json'),
    ]
    
    # 歷史文件
    import glob
    history_files = glob.glob(os.path.join(base_dir, 'web', 'history', 'picks_*.json'))
    
    # Scripts 目錄文件
    scripts_files = [
        os.path.join(base_dir, 'scripts', 'data', 'bursa', 'picks', 'picks_latest.json'),
        os.path.join(base_dir, 'scripts', 'data', 'bursa', 'picks', 'latest_price.json'),
    ]
    
    # 合併所有文件
    all_files = web_files + history_files + scripts_files
    
    # 只保留存在的文件
    existing_files = [f for f in all_files if os.path.exists(f)]
    
    print(f"找到 {len(existing_files)} 個文件需要檢查\n")
    
    # 修復每個文件
    success_count = 0
    for filepath in existing_files:
        relative_path = os.path.relpath(filepath, base_dir)
        print(f"[{success_count + 1}/{len(existing_files)}] {relative_path}")
        
        if fix_file(filepath):
            success_count += 1
        
        print()
    
    print("="*50)
    print(f"📊 總結:")
    print(f"  總文件數: {len(existing_files)}")
    print(f"  成功修復: {success_count}")
    print(f"  失敗: {len(existing_files) - success_count}")
    print("="*50)

if __name__ == "__main__":
    main()
