#!/usr/bin/env python3
"""
正確修復 JSON 文件中的股票代碼格式
"""

import os
import json
import glob
import re

def clean_code(code):
    """清理單個代碼"""
    if code is None:
        return ""
    
    # 轉為字符串
    code_str = str(code)
    
    # 移除 Excel 公式格式
    code_str = code_str.strip()
    if code_str.startswith('="') and code_str.endswith('"'):
        code_str = code_str[2:-1]
    elif code_str.startswith('='):
        code_str = code_str[1:]
    
    # 移除所有不需要的字符（使用正確的轉義）
    # 移除：等號、空格、雙引號、單引號、反斜杠
    code_str = re.sub(r'[=\s"\'\\\\]', '', code_str)
    
    # 補齊前導零
    if code_str.isdigit():
        code_str = code_str.zfill(4)
    
    return code_str

def fix_json_file(filepath):
    """修復單個 JSON 文件"""
    print(f"📝 修復文件: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # 修復 picks 列表
        if 'picks' in data:
            for pick in data['picks']:
                if 'code' in pick:
                    old_code = pick['code']
                    new_code = clean_code(old_code)
                    if old_code != new_code:
                        pick['code'] = new_code
                        modified = True
                        print(f"  🔄 {old_code} → {new_code}")
        
        # 修復 stocks 列表（如果是 latest_price.json）
        if 'stocks' in data:
            for stock in data['stocks']:
                if 'code' in stock:
                    old_code = stock['code']
                    new_code = clean_code(old_code)
                    if old_code != new_code:
                        stock['code'] = new_code
                        modified = True
                        print(f"  🔄 {old_code} → {new_code}")
        
        if modified:
            # 備份原文件
            backup_path = f"{filepath}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 保存修復後的文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 已修復並備份到 {backup_path}")
        else:
            print(f"  ✅ 無需修復")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 修復失敗: {e}")
        return False

def main():
    """主函數"""
    print("="*60)
    print("🛠️  JSON 股票代碼修復工具")
    print("="*60)
    
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定義要修復的文件
    files_to_fix = []
    
    # 1. web 目錄下的文件
    web_dir = os.path.join(current_dir, '..', 'web')
    web_files = [
        os.path.join(web_dir, 'picks_latest.json'),
        os.path.join(web_dir, 'latest_price.json'),
        *glob.glob(os.path.join(web_dir, 'history', 'picks_*.json'))
    ]
    files_to_fix.extend(web_files)
    
    # 2. scripts 目錄下的文件
    scripts_files = [
        os.path.join(current_dir, 'data', 'bursa', 'picks', 'picks_latest.json'),
        os.path.join(current_dir, 'data', 'bursa', 'picks', 'latest_price.json')
    ]
    files_to_fix.extend(scripts_files)
    
    # 過濾存在的文件
    existing_files = [f for f in files_to_fix if os.path.exists(f)]
    
    print(f"找到 {len(existing_files)} 個需要檢查的文件")
    
    for filepath in existing_files:
        fix_json_file(filepath)
        print()
    
    print("="*60)
    print("🎉 修復完成！")
    print("="*60)

if __name__ == "__main__":
    main()
