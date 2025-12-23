#!/bin/bash
# fix_json_tomorrow.sh - scripts目录专用修复脚本

echo "🔧 修复所有JSON文件格式"
echo "时间: $(date '+%H:%M:%S')"
echo ""

# 备份目录
BACKUP_DIR="/storage/emulated/0/bursasearch/myx_shop/backups/tomorrow_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 修复函数
fix_json_file() {
    local file="$1"
    if [ -f "$file" ]; then
        # 备份
        cp "$file" "$BACKUP_DIR/$(basename $file)"
        
        # 修复
        sed -i 's/"code": "=\\"\([0-9]\+\)\\""/"code": "\1"/g' "$file"
        sed -i 's/"code": "=\"\([0-9]\+\)\""/"code": "\1"/g' "$file"
        sed -i 's/"=\"\([0-9A-Z]\+\)\""/"\1"/g' "$file"
        sed -i 's/"=\"\([0-9A-Z]\+\)\",/"\1",/g' "$file"
        
        echo "  ✅ 修复: $(basename $file)"
    fi
}

# 修复scripts目录
echo "修复scripts目录："
cd /storage/emulated/0/bursasearch/myx_shop/scripts
for json_file in *.json 2>/dev/null; do
    fix_json_file "$json_file"
done

# 修复web目录
echo -e "\n修复web目录："
cd /storage/emulated/0/bursasearch/myx_shop
if [ -d "web" ]; then
    for json_file in web/*.json web/history/*.json 2>/dev/null; do
        fix_json_file "$json_file"
    done
fi

# 修复data/json目录
echo -e "\n修复data/json目录："
if [ -d "data/json" ]; then
    for json_file in data/json/*.json 2>/dev/null; do
        fix_json_file "$json_file"
    done
fi

echo -e "\n✅ 修复完成！"
echo "📦 备份位置: $BACKUP_DIR"
echo ""
echo "💡 验证修复："
echo "  grep -r '=\"6742\"' scripts/ web/ data/json/ 2>/dev/null || echo '✅ 无问题'"
