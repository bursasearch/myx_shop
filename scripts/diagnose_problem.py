#!/usr/bin/env python3
import os
import sys
import csv

def diagnose():
    print("=== 诊断问题 ===")
    
    # 1. 检查文件是否存在
    test_file = "/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/20251223.csv"
    print(f"1. 检查测试文件: {test_file}")
    print(f"   存在: {os.path.exists(test_file)}")
    
    if os.path.exists(test_file):
        print(f"   大小: {os.path.getsize(test_file)} 字节")
        print(f"   权限: {oct(os.stat(test_file).st_mode)[-3:]}")
    
    # 2. 检查配置文件
    config_file = "eod_config.json"
    print(f"\n2. 检查配置文件: {config_file}")
    print(f"   存在: {os.path.exists(config_file)}")
    
    if os.path.exists(config_file):
        import json
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"   有效JSON: 是")
            print(f"   Schema列数: {len(config.get('schema', []))}")
            print(f"   Sector映射数: {len(config.get('sector_lookup', {}))}")
        except Exception as e:
            print(f"   有效JSON: 否 - {e}")
    
    # 3. 尝试读取CSV文件
    print(f"\n3. 尝试读取CSV文件...")
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        print(f"   成功读取行数: {len(rows)}")
        if rows:
            print(f"   标题行: {rows[0]}")
            print(f"   列数: {len(rows[0])}")
            print(f"   第一行数据: {rows[1][:5]}..." if len(rows) > 1 else "   无数据行")
    except Exception as e:
        print(f"   读取失败: {e}")
    
    # 4. 检查Python环境
    print(f"\n4. Python环境检查:")
    print(f"   Python版本: {sys.version}")
    print(f"   编码: {sys.getdefaultencoding()}")
    
    # 5. 尝试直接运行normalize脚本
    print(f"\n5. 尝试直接运行normalize_eod.py...")
    try:
        # 创建一个简单的测试
        import subprocess
        result = subprocess.run(
            [sys.executable, "normalize_eod.py", "--help"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   脚本可以执行")
        else:
            print(f"   脚本执行失败: {result.stderr}")
    except Exception as e:
        print(f"   测试失败: {e}")

if __name__ == "__main__":
    diagnose()
