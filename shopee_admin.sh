#!/data/data/com.termux/files/usr/bin/bash

echo "========================================"
echo "   🛍️  Shopee 产品管理系统"
echo "========================================"

# 检查数据文件
echo "📁 检查数据文件:"
if [ -f "js/shopee_lists.json" ]; then
  count=$(grep -c '"name"' js/shopee_lists.json 2>/dev/null || echo "0")
  echo "  ✅ js/shopee_lists.json 存在 ($count 个产品)"
else
  echo "  ❌ js/shopee_lists.json 不存在"
fi

if [ -f "admin/shopee_products.json" ]; then
  count=$(grep -c '"id"' admin/shopee_products.json 2>/dev/null || echo "0")
  echo "  ✅ admin/shopee_products.json 存在 ($count 个产品)"
else
  echo "  ⚠️  admin/shopee_products.json 不存在"
fi

# 运行数据转换
echo -e "\n🔧 转换数据格式..."
if python3 admin/shopee_adapter_fixed.py; then
  echo "✅ 数据转换完成"
else
  echo "⚠️  数据转换可能有问题"
fi

echo ""
echo "🌐 访问地址:"
echo "  • http://127.0.0.1:5000/admin/shopee_simple.html"
echo "  • http://127.0.0.1:5000/admin/shopee_dashboard.html"
echo ""
echo "📱 手机访问:"
IP=$(ip route get 1 2>/dev/null | awk '{print $7;exit}' || echo "127.0.0.1")
echo "  • http://$IP:5000/admin/shopee_simple.html"
echo ""
echo "========================================"
echo "按 Ctrl+C 停止服务器"
echo "========================================"

python3 -m http.server 5000
