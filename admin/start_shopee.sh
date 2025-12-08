#!/data/data/com.termux/files/usr/bin/bash

cd /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop

echo "🛍️ 启动 Shopee 管理后台..."
echo "📁 数据文件:"
echo "  • js/shopee_lists.json (现有数据)"
echo "  • admin/shopee_products.json (转换后的数据)"
echo ""
echo "🌐 访问地址:"
echo "  • http://127.0.0.1:5000/admin/shopee_simple.html (推荐)"
echo "  • http://127.0.0.1:5000/admin/shopee_dashboard.html (原版)"
echo ""
echo "📊 数据统计:"

# 检查现有数据
if [ -f "js/shopee_lists.json" ]; then
  count=$(grep -c '"name"' js/shopee_lists.json 2>/dev/null || echo "0")
  echo "  ✅ js/shopee_lists.json 存在 ($count 个产品)"
else
  echo "  ❌ js/shopee_lists.json 不存在"
fi

# 检查转换后的数据
if [ -f "admin/shopee_products.json" ]; then
  count=$(grep -c '"id"' admin/shopee_products.json 2>/dev/null || echo "0")
  echo "  ✅ admin/shopee_products.json 存在 ($count 个产品)"
else
  echo "  ⚠️  admin/shopee_products.json 不存在，将自动创建"
fi

echo ""
echo "按 Ctrl+C 停止服务器"
echo "----------------------------------------"

python3 -m http.server 5000
