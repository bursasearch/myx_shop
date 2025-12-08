#!/bin/bash
echo "🔧 優化 bursa.html 結構..."
echo "=============================="

cd /storage/emulated/0/bursasearch/myx_shop/web

# 創建目錄
mkdir -p css js components data

# 1. 提取CSS
echo "/* bursa.css - 主樣式 */" > css/bursa.css
grep -A 1000 "<style>" bursa.html | grep -v "<style>" | grep -v "</style>" | head -n -1 >> css/bursa.css

# 2. 提取JavaScript
echo "// bursa.js - 主JavaScript" > js/bursa.js
sed -n '/<script>/,/<\/script>/p' bursa.html | grep -v "<script>" | grep -v "</script>" >> js/bursa.js

# 3. 創建簡化版HTML
cat > bursa_simplified.html << 'HTML_EOF'
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>AI選股分析 | Myx Shop</title>
  <link rel="stylesheet" href="css/bursa.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="preload" href="picks.json" as="fetch">
</head>
<body>
  <div class="container">
    <!-- 導航欄 -->
    <div class="nav-buttons">
      <a href="./index.html" class="nav-btn home-btn"><i class="fas fa-home"></i> 回到主頁</a>
      <a href="stocks.html" class="nav-btn stocks-btn"><i class="fas fa-robot"></i> AI選股回顧</a>
      <a href="retail-inv.html" class="nav-btn retail-btn"><i class="fas fa-users"></i> 散戶特區</a>
      <a href="./products.html" class="nav-btn shop-btn"><i class="fas fa-shopping-bag"></i> 聯盟商店</a>
      <a href="./vehicles.html" class="nav-btn car-btn"><i class="fas fa-car"></i> 二手車輛</a>
    </div>

    <!-- 主要內容由JavaScript動態加載 -->
    <div id="app">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i> 載入AI分析數據中...
      </div>
    </div>
  </div>

  <script src="js/bursa.js"></script>
  <script src="js/connect_ai_data.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function() {
      console.log("🚀 AI選股分析系統啟動");
      const aiConnector = new AIDataConnector();
    });
  </script>
</body>
</html>
HTML_EOF

echo "✅ 優化完成！"
echo "📁 新結構："
find . -type f -name "*.css" -o -name "*.js" -o -name "*.html" | sort
echo ""
echo "💡 建議："
echo "1. 測試 bursa_simplified.html 是否正常"
echo "2. 如果正常，可以替換原文件：mv bursa_simplified.html bursa.html"
echo "3. 訪問 file:///storage/emulated/0/bursasearch/myx_shop/web/bursa.html"
