#!/data/data/com.termux/files/usr/bin/bash

cd /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop

echo "========================================"
echo "   🛍️  Shopee 产品管理系统"
echo "========================================"

# 检查文件
echo "📁 文件状态:"
if [ -f "js/shopee_lists.json" ]; then
  product_count=$(grep -c '"name"' js/shopee_lists.json 2>/dev/null || echo "0")
  echo "  ✅ js/shopee_lists.json ($product_count 个产品)"
else
  echo "  ❌ js/shopee_lists.json 不存在"
fi

if [ -f "admin/shopee_products.json" ]; then
  product_count=$(grep -c '"id"' admin/shopee_products.json 2>/dev/null || echo "0")
  echo "  ✅ admin/shopee_products.json ($product_count 个产品)"
else
  echo "  ❌ admin/shopee_products.json 不存在"
fi

if [ -f "admin/shopee_simple.html" ]; then
  echo "  ✅ admin/shopee_simple.html (管理界面)"
else
  echo "  ❌ admin/shopee_simple.html 不存在"
fi

# 显示产品列表
echo -e "\n📋 产品列表:"
if [ -f "admin/shopee_products.json" ]; then
  python3 -c "
import json
try:
    with open('admin/shopee_products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    products = data.get('products', [])
    for i, p in enumerate(products[:5], 1):
        print(f'  {i}. {p[\"name\"]} - RM{p[\"price\"]}')
    if len(products) > 5:
        print(f'  ... 还有 {len(products)-5} 个产品')
except:
    print('  无法读取产品数据')
"
fi

echo ""
echo "🌐 访问地址:"
echo "  • http://127.0.0.1:5000/admin/shopee_simple.html"
echo "  • http://localhost:5000/admin/shopee_simple.html"
echo ""
echo "📱 手机/平板访问:"
IP=$(ip route get 1 2>/dev/null | awk '{print $NF;exit}' || echo "127.0.0.1")
echo "  • http://$IP:5000/admin/shopee_simple.html"
echo ""
echo "========================================"
echo "按 Ctrl+C 停止服务器"
echo "========================================"

python3 -m http.server 5000
