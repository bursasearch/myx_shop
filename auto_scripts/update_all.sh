#!/data/data/com.termux/files/usr/bin/bash
echo "🔄 更新所有数据..."
cd "/storage/emulated/0/bursasearch/myx_shop"

# 1. 处理EOD数据
echo "📊 处理EOD数据..."
python3 scripts/eod_processor.py

# 2. 生成JSON
echo "🤖 生成AI选股数据..."
python3 scripts/generate_json_from_eod.py

# 3. 更新web数据
echo "🌐 更新web目录..."
python3 scripts/update_web_data.py

echo "✅ 所有数据更新完成！"
