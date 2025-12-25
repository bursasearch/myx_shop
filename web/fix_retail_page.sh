#!/bin/bash
# 修复零售投资页面的数据加载问题

echo "🔧 修复 retail-inv.html 数据加载..."
cd /storage/emulated/0/bursasearch/myx_shop/web

# 备份
cp retail-inv.html retail-inv.html.bak3

# 1. 修复 loadLatestData 函数
echo "1. 修复 loadLatestData 函数..."
LOAD_LATEST_LINE=$(grep -n "function loadLatestData" retail-inv.html | head -1 | cut -d: -f1)
if [ -n "$LOAD_LATEST_LINE" ]; then
    END_LINE=$((LOAD_LATEST_LINE + 20))
    echo "找到 loadLatestData 在第 $LOAD_LATEST_LINE 行"
    
    # 查看当前函数
    sed -n "${LOAD_LATEST_LINE},${END_LINE}p" retail-inv.html
    
    # 替换为修复版本
    cat > temp_fix.js << 'FIX'
        // 加载最新数据
        async function loadLatestData() {
            console.log('🚀 开始加载所有最新数据...');
            
            try {
                // 1. 加载AI选股数据
                console.log('1. 加载AI选股数据...');
                const aiResponse = await fetch('picks_latest.json');
                if (!aiResponse.ok) throw new Error(`AI数据加载失败: ${aiResponse.status}`);
                
                const aiData = await aiResponse.json();
                console.log('✅ AI数据加载成功:', aiData.total_picks, '只股票');
                
                // 提取picks数组
                window.aiStocksData = aiData.picks || [];
                console.log('设置 aiStocksData:', window.aiStocksData.length, '条记录');
                
                // 2. 加载股价数据
                console.log('2. 加载股价数据...');
                const priceResponse = await fetch('latest_price.json');
                if (priceResponse.ok) {
                    const priceData = await priceResponse.json();
                    window.priceData = priceData;
                    console.log('✅ 股价数据加载成功');
                } else {
                    console.warn('⚠️ 股价数据加载失败，继续使用AI数据');
                }
                
                // 3. 更新UI
                if (typeof updateStockDisplay === 'function') {
                    console.log('3. 调用 updateStockDisplay...');
                    updateStockDisplay(window.aiStocksData);
                } else {
                    console.warn('⚠️ updateStockDisplay 函数不存在');
                    // 创建简单显示
                    simpleDisplayStocks(window.aiStocksData);
                }
                
                // 4. 显示成功消息
                showNotification(`成功加载 ${window.aiStocksData.length} 只AI推荐股票`, 'success');
                console.log('🎉 所有数据加载完成');
                
            } catch (error) {
                console.error('❌ 数据加载失败:', error);
                showNotification(`数据加载失败: ${error.message}`, 'error');
                
                // 尝试回退
                tryFallbackData();
            }
        }
        
        // 简单显示股票（备用）
        function simpleDisplayStocks(stocks) {
            console.log('使用简单显示:', stocks.length, '只股票');
            const container = document.getElementById('stock-list') || document.getElementById('aiStocksList');
            if (container) {
                container.innerHTML = '<h3>AI推荐股票列表</h3>';
                stocks.forEach((stock, index) => {
                    const div = document.createElement('div');
                    div.className = 'stock-item';
                    div.innerHTML = `
                        <div style="border:1px solid #ddd; padding:10px; margin:5px; border-radius:5px;">
                            <strong>#${index + 1} ${stock.code} - ${stock.name}</strong><br>
                            <span>价格: RM ${stock.current_price}</span> | 
                            <span>涨跌: ${stock.daily_change}%</span><br>
                            <span>推荐: ${stock.recommendation}</span> | 
                            <span>风险: ${stock.risk_level}</span><br>
                            <small>${stock.potential_reasons}</small>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
        }
        
        // 回退数据
        function tryFallbackData() {
            console.log('尝试回退数据...');
            // 可以在这里添加回退逻辑
            showNotification('正在尝试其他数据源...', 'warning');
        }
FIX
    
    # 替换原函数
    sed -i "${LOAD_LATEST_LINE},${END_LINE}d" retail-inv.html
    sed -i "${LOAD_LATEST_LINE}r temp_fix.js" retail-inv.html
    rm temp_fix.js
    echo "✅ loadLatestData 函数已修复"
else
    echo "❌ 未找到 loadLatestData 函数"
fi

# 2. 确保页面加载时调用正确函数
echo ""
echo "2. 修复页面初始化..."
# 查找DOMContentLoaded事件
DOM_LINE=$(grep -n "DOMContentLoaded" retail-inv.html | head -1 | cut -d: -f1)
if [ -n "$DOM_LINE" ]; then
    echo "找到DOMContentLoaded在第 $DOM_LINE 行"
    
    # 查看初始化代码
    sed -n "${DOM_LINE},$((DOM_LINE + 15))p" retail-inv.html
    
    # 添加更可靠的初始化
    cat > temp_init.js << 'INIT'
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('📱 Bursa AI投资计算器启动');
            console.log('当前URL:', window.location.href);
            
            // 初始化UI
            initUI();
            
            // 绑定事件监听器
            bindEventListeners();
            
            // 立即加载数据（不再延迟）
            console.log('立即加载数据...');
            loadLatestData();
        });
INIT
    
    # 替换初始化部分
    sed -i "${DOM_LINE},$((DOM_LINE + 10))d" retail-inv.html
    sed -i "${DOM_LINE}r temp_init.js" retail-inv.html
    rm temp_init.js
    echo "✅ 页面初始化已修复"
fi

# 3. 添加调试信息
echo ""
echo "3. 添加调试信息..."
# 在文件末尾添加调试函数
cat >> retail-inv.html << 'DEBUG'

<!-- 调试函数 -->
<script>
// 调试函数：检查数据状态
window.debugData = function() {
    console.log('=== 数据状态调试 ===');
    console.log('1. aiStocksData:', window.aiStocksData ? 
        `数组，${window.aiStocksData.length} 条记录` : '未定义');
    
    console.log('2. priceData:', window.priceData ? 
        `对象，${Object.keys(window.priceData).length} 个键` : '未定义');
    
    console.log('3. 当前数据源:', window.currentDataSource || '未设置');
    
    // 测试文件访问
    fetch('picks_latest.json')
        .then(r => r.json())
        .then(data => {
            console.log('4. 直接访问 picks_latest.json:', 
                data.total_picks || data.length, '条记录');
        })
        .catch(e => console.log('4. 文件访问失败:', e));
};

// 手动重新加载数据
window.reloadData = function() {
    console.log('手动重新加载数据...');
    loadLatestData();
};

// 页面加载完成后自动调试
setTimeout(() => {
    console.log('页面加载完成，当前数据状态:');
    debugData();
}, 2000);
</script>
DEBUG

echo "✅ 修复完成！"
echo "现在打开: http://localhost:5050/retail-inv.html"
echo "按 F12 打开控制台查看调试信息"
