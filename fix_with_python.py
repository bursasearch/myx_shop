#!/usr/bin/env python3
import json
import re
import os

def fix_json_file(filepath):
    """修复JSON文件中的错误格式"""
    print(f"处理文件: {os.path.basename(filepath)}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有问题
        if '="' in content:
            print(f"  发现 '=\"' 格式问题")
            
            # 修复 "=\"数字\"" 为 "数字"
            # 修复 "=\"6742\"" → "6742"
            # 修复 "=\"5210\"" → "5210"
            fixed_content = re.sub(r'"="([0-9A-Z]+?)""', r'"\1"', content)
            fixed_content = re.sub(r'"="([0-9A-Z]+?)",', r'"\1",', fixed_content)
            
            # 修复 code字段: "code": "=\"5210\"" → "code": "5210"
            fixed_content = re.sub(r'"code":\s*"=\\"([0-9]+?)\\""', r'"code": "\1"', fixed_content)
            fixed_content = re.sub(r'"code":\s*"="([0-9]+?)""', r'"code": "\1"', fixed_content)
            
            # 保存修复后的内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("  ✅ 已修复格式问题")
            
            # 验证JSON格式
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    json.load(f)
                print("  ✅ JSON格式有效")
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON格式仍有问题: {e}")
        else:
            print("  ✅ 未发现格式问题")
            
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")

# 修复所有有问题的文件
print("🔧 使用Python修复JSON文件格式")
print("===============================")

files_to_fix = [
    "./data/json/picks.json",
    "./data/json/sector_missing.json",
    "./data/json/picks_20251212.json"
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        fix_json_file(filepath)
    else:
        print(f"文件不存在: {filepath}")

print("\n🎉 修复完成！")
