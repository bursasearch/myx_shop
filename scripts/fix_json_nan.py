#!/usr/bin/env python3
"""
修復JSON文件中的NaN值
"""

import json
import sys
import os
import math

def fix_nan_in_json(filepath):
    """修復JSON文件中的NaN值"""
    print(f"🔧 修復文件: {filepath}")
    
    try:
        # 讀取文件
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換NaN值
        fixed_content = content.replace(': NaN', ': null')
        fixed_content = fixed_content.replace(': nan', ': null')
        fixed_content = fixed_content.replace(': "NaN"', ': null')
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ 修復完成: {filepath}")
        
        # 驗證JSON是否有效
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ JSON驗證通過")
        
    except Exception as e:
        print(f"❌ 修復失敗: {e}")

def main():
    if len(sys.argv) > 1:
        files_to_fix = sys.argv[1:]
    else:
        # 默認修復所有JSON文件
        files_to_fix = [
            '../web/latest_price.json',
            '../web/picks_latest.json',
            '../web/history/picks_*.json'
        ]
    
    for file_pattern in files_to_fix:
        if '*' in file_pattern:
            import glob
            for file in glob.glob(file_pattern):
                fix_nan_in_json(file)
        else:
            if os.path.exists(file_pattern):
                fix_nan_in_json(file_pattern)
            else:
                print(f"⚠️ 文件不存在: {file_pattern}")

if __name__ == "__main__":
    main()
