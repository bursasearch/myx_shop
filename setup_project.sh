#!/data/data/com.termux/files/usr/bin/bash

echo "🎯 设置 Bursa Malaysia 项目结构..."

PROJECT_DIR="/storage/emulated/0/bursasearch/myx_shop"

cd "$PROJECT_DIR"

# 1. 确保目录存在
mkdir -p scripts auto_scripts web/history assets/{css,js,images} data/json

# 2. 创建缺失的Python脚本
echo "📝 创建 update_web_data.py..."
if [ ! -f "scripts/update_web_data.py" ]; then
    # 这里放置 update_web_data.py 的内容
    cat > scripts/update_web_data.py << 'PYEOF'
#!/usr/bin/env python3
print("update_web_data.py 内容待填充")
PYEOF
fi

echo "📝 创建 investment_calculator.py..."
if [ ! -f "scripts/investment_calculator.py" ]; then
    # 这里放置 investment_calculator.py 的内容
    cat > scripts/investment_calculator.py << 'PYEOF'
#!/usr/bin/env python3
print("investment_calculator.py 内容待填充")
PYEOF
fi

# 3. 创建自动化脚本
echo "🤖 创建自动化脚本..."

# 完整更新脚本
cat > auto_scripts/update_all.sh << 'BASH_EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "/storage/emulated/0/bursasearch/myx_shop"
echo "🔄 开始完整更新流程..."
python3 scripts/eod_processor.py
python3 scripts/generate_json_from_eod.py
python3 scripts/update_web_data.py
echo "✅ 更新完成！"
BASH_EOF

# 简单更新脚本
cat > auto_scripts/update_web.sh << 'BASH_EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "/storage/emulated/0/bursasearch/myx_shop"
python3 scripts/update_web_data.py
BASH_EOF

# GitHub推送脚本
cat > auto_scripts/push_to_github.sh << 'BASH_EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "/storage/emulated/0/bursasearch/myx_shop"
git add web/*.html web/*.json web/history/*.json
git commit -m "更新: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
BASH_EOF

# 4. 设置权限
chmod +x scripts/*.py auto_scripts/*.sh

# 5. 创建便捷链接
cd ~
ln -sf "$PROJECT_DIR/auto_scripts/update_all.sh" ./bursa_update.sh
ln -sf "$PROJECT_DIR/auto_scripts/push_to_github.sh" ./bursa_push.sh

echo ""
echo "✅ 项目设置完成！"
echo ""
echo "📋 可用命令:"
echo "  ~/bursa_update.sh    - 更新所有数据"
echo "  ~/bursa_push.sh      - 推送到GitHub"
echo "  cd $PROJECT_DIR/scripts && python3 eod_processor.py - 单独运行处理器"
echo ""
echo "🌐 Web文件在: $PROJECT_DIR/web/"
echo "📁 数据文件在: $PROJECT_DIR/data/"
