#!/bin/bash
# 改进的EOD处理器，包含代码修复

echo "📅 今天: $(date '+%Y-%m-%d %A')"

# 路径配置
SOURCE="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/25251230.csv"
WORKDIR="/storage/emulated/0/bursasearch/myx_shop/scripts"
DATA_DATE="20251230"

if [ ! -f "$SOURCE" ]; then
    echo "❌ 找不到文件: $SOURCE"
    echo "🔍 尝试查找其他文件..."
    
    # 查找最新的CSV文件
    EOD_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
    LATEST=$(ls -t "$EOD_DIR"/*.csv 2>/dev/null | head -1)
    
    if [ -f "$LATEST" ]; then
        SOURCE="$LATEST"
        echo "✅ 使用最新文件: $(basename "$SOURCE")"
    else
        exit 1
    fi
fi

cd "$WORKDIR" || exit 1

echo ""
echo "📁 处理: $(basename "$SOURCE")"
cp "$SOURCE" .

# 运行Python生成JSON
echo ""
echo "▶️  运行Python脚本..."
python3 generate_json_from_eod.py "$(basename "$SOURCE")"

if [ $? -ne 0 ]; then
    echo "❌ Python脚本执行失败"
    exit 1
fi

echo ""
echo "🔧 修复股票代码格式..."

# 创建修复脚本
cat > temp_fix.py << 'PYFIX'
import json, re, os

def fix_code(code):
    if not isinstance(code, str):
        return code
    code = re.sub(r'^[=\s"\']+', '', code)
    code = re.sub(r'[\s"\']+$', '', code)
    code = re.sub(r'\s*-\s*CW\w*$', '', code, flags=re.I)
    code = code.strip().upper()
    
    # 特殊修复
    fixes = {
        "0652MR": "0652",
        "HSI-CWMR": "HSICW",
        "=\\"0652\\"": "0652",
    }
    
    return fixes.get(code, code)

def fix_file(filepath):
    if not os.path.exists(filepath):
        return 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return 0
    
    fixed = 0
    def fix_obj(obj):
        nonlocal fixed
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if key.lower() in ['code', 'stock_code'] and isinstance(value, str):
                    new_val = fix_code(value)
                    if new_val != value:
                        obj[key] = new_val
                        fixed += 1
                elif isinstance(value, (dict, list)):
                    fix_obj(value)
        elif isinstance(obj, list):
            for item in obj:
                fix_obj(item)
    
    fix_obj(data)
    
    if fixed > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return fixed

# 修复文件
files = ["picks_latest.json", "latest_price.json", "data.json"]
total = 0
for f in files:
    if os.path.exists(f):
        fixed = fix_file(f)
        total += fixed
        if fixed > 0:
            print(f"✅ {f}: 修复 {fixed} 个代码")

print(f"总共修复了 {total} 个股票代码")
PYFIX

python3 temp_fix.py
rm -f temp_fix.py

# 确保目录存在
mkdir -p history ../web/history

echo ""
echo "📁 保存文件..."

# 处理文件
if [ -f "picks_latest.json" ]; then
    # 历史文件
    cp picks_latest.json "history/picks_${DATA_DATE}.json"
    echo "✅ 历史: picks_${DATA_DATE}.json"
    
    # 复制到web
    cp picks_latest.json latest_price.json data.json ../web/ 2>/dev/null
    cp "history/picks_${DATA_DATE}.json" ../web/history/ 2>/dev/null
    
    echo "✅ 复制到web目录"
    
    # 显示摘要
    echo ""
    echo "📊 处理摘要:"
    echo "  数据日期: ${DATA_DATE:0:4}-${DATA_DATE:4:2}-${DATA_DATE:6:2}"
    
    # 显示一些股票代码示例
    echo ""
    echo "📈 股票代码示例:"
    if [ -f "picks_latest.json" ]; then
        grep -o '"code": *"[^"]*"' picks_latest.json | head -5 | sed 's/"code": "/  /g; s/"$//g'
    fi
    
    echo ""
    echo "🎉 处理完成！"
    echo "⏰ 时间: $(date '+%H:%M:%S')"
else
    echo "⚠️  未生成 picks_latest.json"
fi
