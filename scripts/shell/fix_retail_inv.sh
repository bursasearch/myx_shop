#!/bin/bash
echo "开始修复 retail-inv.html..."

# 备份原文件
cp retail-inv.html retail-inv-backup.html

# 1. 修复API端点（从 /calc-profit 改为 /run-backtest）
sed -i 's|/calc-profit|/run-backtest|g' retail-inv.html

# 2. 修复导航链接（使用相对路径）
sed -i 's|href="/"|href="index.html"|g' retail-inv.html
sed -i 's|href="/stocks.html"|href="stocks.html"|g' retail-inv.html

# 3. 修改API请求格式以匹配 run-backtest
# 原格式需要修改为 api.py 期望的格式
sed -i "s|'stock_code': document.getElementById('stock_code').value,|'stocks': [document.getElementById('stock_code').value + '.KL'],|g" retail-inv.html
sed -i "s|'initial_investment': document.getElementById('initial_investment').value|'capital': document.getElementById('initial_investment').value|g" retail-inv.html

# 4. 修改结果显示逻辑以匹配 run-backtest 的返回格式
# 在脚本部分添加新函数
cat >> retail-inv.html << 'JS_EOF'

// 修改 displayResults 函数以匹配 run-backtest API
function displayResultsNew(data) {
    // 更新股票名称
    document.getElementById('stockName').textContent = 
        `股票回测结果`;
    
    // 检查API返回的数据结构
    console.log('API返回数据:', data);
    
    if (data.portfolio && data.portfolio.length > 0) {
        const initialInvestment = parseFloat(document.getElementById('initial_investment').value);
        const finalValue = data.metrics?.final_value || data.portfolio[data.portfolio.length - 1];
        const profitLoss = finalValue - initialInvestment;
        const profitLossPercent = ((profitLoss / initialInvestment) * 100).toFixed(2);
        
        // 更新主要数据
        document.getElementById('currentValue').textContent = `RM ${finalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('profitLoss').textContent = `RM ${profitLoss.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('profitLossPercent').textContent = `${profitLossPercent}%`;
        document.getElementById('holdingDays').textContent = `${data.dates ? data.dates.length : 'N/A'} 天`;
        
        // 设置颜色
        const profitLossElem = document.getElementById('profitLoss');
        const percentElem = document.getElementById('profitLossPercent');
        
        if (profitLoss >= 0) {
            profitLossElem.className = 'stat-value profit';
            percentElem.className = 'stat-value profit';
        } else {
            profitLossElem.className = 'stat-value loss';
            percentElem.className = 'stat-value loss';
        }
        
        // 显示详细结果
        const detailedHTML = `
            <p><strong>📈 回测类型:</strong> 股票投资组合回测</p>
            <p><strong>📊 总回报率:</strong> ${data.metrics?.total_return ? data.metrics.total_return.toFixed(2) + '%' : 'N/A'}</p>
            <p><strong>📈 年化回报:</strong> ${data.metrics?.annual_return ? data.metrics.annual_return.toFixed(2) + '%' : 'N/A'}</p>
            <p><strong>📉 最大回撤:</strong> ${data.metrics?.max_drawdown ? data.metrics.max_drawdown.toFixed(2) + '%' : 'N/A'}</p>
            <p><strong>📅 数据点数:</strong> ${data.portfolio ? data.portfolio.length : 0} 个交易日</p>
            <p><strong>✅ 回测状态:</strong> 成功完成</p>
        `;
        document.getElementById('detailedResults').innerHTML = detailedHTML;
        
        // 显示结果区域
        document.getElementById('results').classList.remove('hidden');
        
        // 滚动到结果区域
        document.getElementById('results').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    } else {
        showError('回测数据格式不正确');
    }
}

// 修改表单提交处理
document.getElementById('backtestForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('calculateBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('errorMessage');
    
    // 显示加载中
    btn.disabled = true;
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    error.classList.add('hidden');
    
    try {
        const stockCode = document.getElementById('stock_code').value;
        // 确保股票代码有 .KL 后缀
        const formattedStockCode = stockCode.includes('.') ? stockCode : stockCode + '.KL';
        
        const formData = {
            stocks: [formattedStockCode],
            start_date: document.getElementById('start_date').value,
            capital: parseFloat(document.getElementById('initial_investment').value)
        };
        
        console.log('提交数据:', formData);
        
        const response = await fetch('/run-backtest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        console.log('API响应:', data);
        
        if (data.success) {
            displayResultsNew(data);
        } else {
            showError(data.error || '回测失败');
        }
    } catch (error) {
        console.error('Fetch错误:', error);
        showError('网络错误，请检查服务器连接后重试');
    } finally {
        btn.disabled = false;
        loading.classList.add('hidden');
    }
});
JS_EOF

echo "✅ 修复完成！"
echo "主要修改："
echo "1. API端点从 /calc-profit 改为 /run-backtest"
echo "2. 修复了导航链接"
echo "3. 调整了数据格式以匹配 api.py"
echo "4. 更新了结果显示逻辑"
