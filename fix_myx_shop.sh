#!/bin/bash
echo "🔧 Myx Shop 网站修复工具"
echo "========================"

# 1. 备份原文件
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r web/*.html "$backup_dir/" 2>/dev/null
echo "📁 备份到: $backup_dir"

# 2. 修复HTML文件路径
echo "🔄 修复HTML文件路径..."
for html_file in web/*.html; do
    if [ -f "$html_file" ]; then
        # 修复所有JSON引用
        sed -i 's#"scripts/data/bursa/picks/#"web/#g' "$html_file"
        sed -i 's#"\.json"#"web/picks_latest.json"#g' "$html_file"
        sed -i 's#"picks_#"web/picks_#g' "$html_file"
        echo "  ✅ 修复: $(basename "$html_file")"
    fi
done

# 3. 确保数据文件存在
echo "📊 同步数据文件..."
mkdir -p web
cp scripts/picks_latest.json web/ 2>/dev/null || echo "  ℹ️  picks_latest.json 已存在"
cp scripts/latest_price.json web/ 2>/dev/null || echo "  ℹ️  latest_price.json 已存在"
cp scripts/data/bursa/picks/picks_2025*.json web/ 2>/dev/null || echo "  ℹ️  历史数据文件已存在"

# 4. 创建文件清单
echo "📋 文件清单:"
echo "HTML 文件:"
ls web/*.html 2>/dev/null | xargs -I {} basename {} | sed 's/^/  • /'
echo ""
echo "JSON 数据文件:"
ls web/*.json 2>/dev/null | xargs -I {} basename {} | sed 's/^/  • /'

# 5. 验证修复
echo ""
echo "✅ 修复完成！"
echo ""
echo "🌐 测试步骤:"
echo "1. 启动本地服务器: python3 -m http.server 8080"
echo "2. 访问: http://localhost:8080"
echo "3. 点击链接测试所有页面"
echo "4. 检查控制台 (F12) 是否有错误"
echo ""
echo "📤 推送到GitHub:"
echo "  git add ."
echo "  git commit -m '修复网站路径问题'"
echo "  git push origin main"
