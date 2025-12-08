#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import shutil
import os
from datetime import datetime
from pathlib import Path

def main():
    print("開始更新網站數據...")
    
    # 路徑
    src_dir = Path("/storage/shared/bursasearch/myx_shop/scripts/data")
    dst_dir = Path("/storage/shared/bursasearch/myxshop")
    
    # 確保目標目錄存在
    dst_dir.mkdir(exist_ok=True)
    
    # 要複製的文件
    files_to_copy = [
        ("picks.json", True),        # 需要更新時間戳
        ("backtest_report.json", True),
        ("ai_analysis_preview.html", False)  # 直接複製
    ]
    
    for filename, update_timestamp in files_to_copy:
        src_file = src_dir / filename
        dst_file = dst_dir / filename
        
        if not src_file.exists():
            print(f"⚠️  找不到: {src_file}")
            continue
        
        if update_timestamp:
            # 處理JSON文件
            try:
                with open(src_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['website_update'] = datetime.now().isoformat()
                
                with open(dst_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ 已更新: {filename}")
            except Exception as e:
                print(f"❌ 處理 {filename} 失敗: {e}")
        else:
            # 直接複製
            try:
                shutil.copy2(src_file, dst_file)
                print(f"✅ 已複製: {filename}")
            except Exception as e:
                print(f"❌ 複製 {filename} 失敗: {e}")
    
    print("\n🎉 更新完成!")
    print(f"文件位置: {dst_dir}")
    
    # 列出所有文件
    print("\n📁 目錄內容:")
    for item in dst_dir.iterdir():
        if item.is_file():
            size = item.stat().st_size
            print(f"  {item.name} ({size} bytes)")

if __name__ == "__main__":
    main()
