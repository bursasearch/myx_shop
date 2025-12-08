#!/bin/bash
echo "🔗 修復bursa.html鏈接..."
echo "=============================="

# 備份原文件
cp bursa.html bursa.html.backup.$(date +%Y%m%d_%H%M)

# 更新AI分析報告鏈接（如果存在）
if grep -q "ai_analysis_preview.html" bursa.html; then
    echo "✅ bursa.html已經鏈接到AI報告"
else
    # 添加AI報告鏈接
    sed -i '/<div class="stock-grid">/i\
    <!-- AI分析報告 -->\
    <div class="video-section" style="text-align:center; margin:2rem 0;">\
      <h2><i class="fas fa-chart-line"></i> 完整AI分析報告</h2>\
      <p>查看完整的AI選股分析和回測報告：</p>\
      <a href="web/ai_analysis_preview.html" class="nav-btn stocks-btn" style="display:inline-flex; margin:1rem;">\
        <i class="fas fa-robot"></i> 查看完整AI報告\
      </a>\
    </div>' bursa.html
    echo "✅ 已添加AI報告鏈接"
fi

# 檢查是否需要更新其他鏈接
echo ""
echo "🔍 檢查鏈接："
echo "- retail-inv.html: $(grep -c 'retail-inv.html' bursa.html) 處引用"
echo "- products.html: $(grep -c 'products.html' bursa.html) 處引用"
echo "- vehicles.html: $(grep -c 'vehicles.html' bursa.html) 處引用"
echo "- web/ 目錄: $(grep -c 'web/' bursa.html) 處引用"

echo ""
echo "✅ 鏈接修復完成"
