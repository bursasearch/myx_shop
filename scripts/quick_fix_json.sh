#!/bin/bash
# 快速修复JSON文件中的股票代码

echo "🔧 快速修复JSON股票代码"
echo "======================"

cd /storage/emulated/0/bursasearch/myx_shop/scripts

# 创建临时Python修复脚本
cat > temp_quick_fix.py << 'PYCODE'
import json, re, os, sys

def fix_all_files():
    # 需要修复的文件
    files = [
        "picks_latest.json",
        "latest_price.json",
        "data.json"
    ]
    
    # 修复函数
    def fix_code(code):
        if not isinstance(code, str):
            return code
        
        # 移除等号和引号
        code = re.sub(r'^[=\'"\s]+', '', code)
        code = re.sub(r'[\'"\s]+$', '', code)
        
        # 移除后缀
        code = re.sub(r'\s*-\s*(CW|CA|CF|CR|H|MR|WB)\s*$', '', code, flags=re.I)
        
        # 特殊处理
        if code == "0652MR":
            return "0652"
        elif code == "HSI-CWMR":
            return "HSICW"
        elif '="' in code:
            # 清理 ="0652" 格式
            code = re.sub(r'="([^"]+)"', r'\1', code)
        
        return code.strip().upper()
    
    total_fixed = 0
    
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"❌ 跳过: {filepath} (不存在)")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed = 0
            
            def fix_obj(obj):
                nonlocal fixed
                if isinstance(obj, dict):
                    for key, value in list(obj.items()):
                        if key.lower() == 'code' and isinstance(value, str):
                            new_value = fix_code(value)
                            if new_value != value:
                                obj[key] = new_value
                                fixed += 1
                                if fixed <= 3:
                                    print(f"    {value} → {new_value}")
                        elif isinstance(value, (dict, list)):
                            fix_obj(value)
                elif isinstance(obj, list):
                    for item in obj:
                        fix_obj(item)
            
            fix_obj(data)
            
            if fixed > 0:
                # 保存修复后的文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {filepath}: 修复 {fixed} 个代码")
                total_fixed += fixed
            else:
                print(f"✓ {filepath}: 无需修复")
                
        except Exception as e:
            print(f"❌ {filepath}: 错误 - {e}")
    
    return total_fixed

if __name__ == "__main__":
    print("开始修复股票代码...")
    fixed = fix_all_files()
    print(f"\n总共修复了 {fixed} 个股票代码")
PYCODE

echo "▶️  运行修复脚本..."
python3 temp_quick_fix.py

rm -f temp_quick_fix.py

echo ""
echo "✅ 修复完成！"
