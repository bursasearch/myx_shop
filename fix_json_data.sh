#!/data/data/com.termux/files/usr/bin/bash
# 精准修复JSON数据中的错误股票代码格式

cd /storage/emulated/0/bursasearch/myx_shop

echo "🎯 精准修复股票代码格式错误"
echo "==============================="
echo "修复目标:"
echo "1. picks.json 中的 =\"5210\" 等问题"
echo "2. sector_missing.json 中的 =\"6742\" 等问题"
echo ""

# 备份
BACKUP_DIR="backups/json_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp ./data/json/picks.json "$BACKUP_DIR/" 2>/dev/null
cp ./data/json/sector_missing.json "$BACKUP_DIR/" 2>/dev/null
cp ./data/json/picks_20251212.json "$BACKUP_DIR/" 2>/dev/null
echo "✅ 已创建备份到: $BACKUP_DIR"

# 修复函数
fix_json_format() {
    local file="$1"
    echo -e "\n处理文件: $(basename "$file")"
    
    if [ ! -f "$file" ]; then
        echo "  ❌ 文件不存在"
        return
    fi
    
    # 检查问题
    PROBLEM_COUNT=$(grep -c '=\"[0-9]' "$file" || echo "0")
    if [ "$PROBLEM_COUNT" -gt 0 ]; then
        echo "  发现 $PROBLEM_COUNT 处格式错误"
        
        # 创建临时备份
        cp "$file" "$file.temp_bak"
        
        # 精准修复：只针对 "=\"数字" 模式
        # 修复 "=\"5210\"" → "5210"
        sed -i 's/"=\\"\([0-9]\+\)\\""/"\1"/g' "$file"  # 先处理转义版本
        sed -i 's/"=\"\([0-9]\+\)\""/"\1"/g' "$file"    # 再处理普通版本
        
        # 修复 "=\"6742\"," → "6742",
        sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$file"
        
        # 修复 code 字段的特定问题
        sed -i 's/"code": "=\"\([0-9]\+\)\"/"code": "\1"/g' "$file"
        
        echo "  ✅ 已修复格式错误"
        
        # 显示修复前后的对比
        echo "  修复前后示例:"
        grep -n '=\"[0-9]' "$file.temp_bak" | head -2 | while read line; do
            echo "    修复前: $line"
        done
        echo "    修复后: 格式已纠正"
        
        rm "$file.temp_bak"
    else
        echo "  ✅ 未发现格式错误"
    fi
}

# 开始修复
echo -e "\n开始修复..."
fix_json_format "./data/json/picks.json"
fix_json_format "./data/json/sector_missing.json"
fix_json_format "./data/json/picks_20251212.json"

# 验证修复结果
echo -e "\n🔍 验证修复结果:"
echo "检查 picks.json 中的股票代码:"
grep -n '"code"' ./data/json/picks.json | head -5

echo -e "\n检查 sector_missing.json 中的6742:"
grep -n "6742" ./data/json/sector_missing.json | head -3

echo -e "\n验证JSON格式有效性:"
for file in ./data/json/picks.json ./data/json/sector_missing.json; do
    if python3 -m json.tool "$file" >/dev/null 2>&1; then
        echo "  ✅ $(basename "$file"): JSON格式有效"
    else
        echo "  ❌ $(basename "$file"): JSON格式有问题"
    fi
done

echo -e "\n🎉 修复完成！"
echo "📋 下一步:"
echo "  1. 刷新网页查看6742是否显示正常"
echo "  2. 如果仍有问题，检查网页实际加载的是哪个JSON文件"
echo "  3. 如需恢复: cp $BACKUP_DIR/* ./data/json/"
