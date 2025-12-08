#!/data/data/com.termux/files/usr/bin/bash

cd /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop

echo "========================================"
echo "   🛍️  Shopee 管理后台"
echo "========================================"

echo "📁 可用管理界面:"
echo "  1. http://127.0.0.1:5000/admin/shopee_icon.html   (图标版)"
echo "  2. http://127.0.0.1:5000/admin/shopee_simple.html (图片版)"
echo "  3. http://127.0.0.1:5000/admin/shopee_manager.html (简洁版)"
echo "  4. http://127.0.0.1:5000/admin/index.html         (索引页)"

echo -e "\n📊 数据统计:"
if [ -f "admin/shopee_products.json" ]; then
  count=$(grep -c '"id"' admin/shopee_products.json 2>/dev/null || echo "0")
  echo "  • 产品数量: $count"
  
  # 显示分类统计
  echo "  • 分类分布:"
  python3 -c "
import json
try:
    with open('admin/shopee_products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = {}
    for p in data.get('products', []):
        cat = p.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in categories.items():
        cat_names = {'health': '保健', 'home': '家居', 'electronic': '电子', 'book': '图书'}
        print(f'    - {cat_names.get(cat, cat)}: {count}')
except:
    print('   无法读取分类数据')
"
fi

echo ""
echo "🌐 快速访问:"
echo "  手机浏览器访问:"
IP=$(ip route get 1 2>/dev/null | awk '{print $NF;exit}' || echo "127.0.0.1")
echo "  • http://$IP:5000/admin/shopee_icon.html"
echo ""
echo "========================================"
echo "按 Ctrl+C 停止服务器"
echo "========================================"

python3 -m http.server 5000
