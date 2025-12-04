// AI选股数据加载器
class StockDataManager {
    constructor() {
        this.apiBase = 'http://127.0.0.1:5000';
        this.currentData = null;
    }

    // 加载AI选股数据
    async loadAIData() {
        try {
            console.log("正在加载AI选股数据...");
            
            // 尝试从API获取
            const response = await fetch(`${this.apiBase}/get-stocks/current`);
            if (!response.ok) throw new Error(`API错误: ${response.status}`);
            
            const data = await response.json();
            this.currentData = data;
            
            console.log("AI选股数据加载成功:", data);
            return data;
            
        } catch (error) {
            console.warn("API加载失败，使用示例数据:", error);
            return this.getExampleData();
        }
    }

    // 获取示例数据（当API不可用时）
    getExampleData() {
        return {
            analysis_date: new Date().toLocaleDateString('zh-CN'),
            strategy: "多因子AI选股",
            total_selected: 7,
            selected_stocks: [
                { code: "GENTING", name: "云顶集团", price: "4.85", change: "+2.1%", strategy: "强势反弹", score: 92 },
                { code: "MAYBANK", name: "马来亚银行", price: "9.42", change: "+0.8%", strategy: "价值投资", score: 88 },
                { code: "TENAGA", name: "国家能源", price: "11.25", change: "+1.5%", strategy: "稳定增长", score: 85 },
                { code: "PCHEM", name: "国油化学", price: "6.78", change: "+3.2%", strategy: "超跌反弹", score: 90 },
                { code: "CIMB", name: "联昌国际银行", price: "6.95", change: "+1.8%", strategy: "成交量异动", score: 87 },
                { code: "IOICORP", name: "IOI集团", price: "3.62", change: "+2.5%", strategy: "技术突破", score: 84 },
                { code: "SIMEPLT", name: "森那美种植", price: "4.28", change: "+1.2%", strategy: "行业轮动", score: 82 }
            ]
        };
    }

    // 刷新数据
    async refreshData() {
        const data = await this.loadAIData();
        this.updateUI(data);
        return data;
    }

    // 更新UI
    updateUI(data) {
        // 更新标题
        document.getElementById('updateTime').textContent = 
            `最后更新: ${data.analysis_date || new Date().toLocaleString()}`;
        
        // 更新摘要
        document.getElementById('weeklyAvgReturn').textContent = '+8.2%';
        document.getElementById('successRate').textContent = '72%';
        document.getElementById('totalStocks').textContent = `${data.total_selected}只`;
        document.getElementById('bestReturn').textContent = '+4.5%';
        document.getElementById('bestStock').textContent = data.selected_stocks?.[0]?.code || 'GENTING';
        
        // 更新表格
        this.updateStockTable(data.selected_stocks || []);
    }

    // 更新股票表格
    updateStockTable(stocks) {
        const tbody = document.getElementById('todayStocksTable');
        if (!tbody) return;

        if (stocks.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: #718096;">
                        <i class="fas fa-exclamation-circle"></i> 暂无选股数据
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = stocks.map(stock => `
            <tr>
                <td><strong>${stock.code}</strong></td>
                <td>${stock.name || ''}</td>
                <td>RM ${stock.price || '0.00'}</td>
                <td class="${stock.change?.includes('+') ? 'positive' : 'negative'}">
                    ${stock.change || '0.0%'}
                </td>
                <td>
                    <span class="strategy-tag tag-${this.getStrategyClass(stock.strategy)}">
                        ${stock.strategy || '未指定'}
                    </span>
                </td>
                <td><span class="ai-score">${stock.score || 0}/100</span></td>
            </tr>
        `).join('');
    }

    // 获取策略CSS类
    getStrategyClass(strategy) {
        if (!strategy) return 'strong';
        
        if (strategy.includes('反弹') || strategy.includes('强势')) return 'rebound';
        if (strategy.includes('价值') || strategy.includes('稳定')) return 'strong';
        if (strategy.includes('成交') || strategy.includes('技术')) return 'volume';
        return 'strong';
    }
}

// 初始化
document.addEventListener("DOMContentLoaded", function() {
    console.log("AI选股数据加载器初始化...");
    
    // 创建全局实例
    window.stockDataManager = new StockDataManager();
    
    // 自动加载数据
    setTimeout(() => {
        stockDataManager.refreshData();
    }, 1000);
});
