// stock_data_loader.js
class StockDataManager {
  constructor() {
    this.todayStocks = [];
    this.weeklyPerformance = {};
    this.cacheDuration = 5 * 60 * 1000; // 5分鐘快取
    this.init();
  }

  async init() {
    console.log('📊 初始化股票數據管理器...');
    await this.loadAllData();
    this.setupAutoRefresh();
  }

  async loadAllData() {
    try {
      await Promise.all([
        this.loadTodayStocks(),
        this.loadWeeklyPerformance()
      ]);
      
      this.renderAll();
      this.updateLastUpdateTime();
      
    } catch (error) {
      console.error('載入數據失敗:', error);
      this.showError();
    }
  }

  async loadTodayStocks() {
    try {
      const response = await fetch('website_data/ai_stocks_latest.json?v=' + Date.now());
      const data = await response.json();
      
      if (data && data.stocks) {
        this.todayStocks = data.stocks;
        console.log(`✅ 載入今日選股: ${this.todayStocks.length} 支`);
        
        // 保存到localStorage
        localStorage.setItem('aiStocksData', JSON.stringify({
          data: data.stocks,
          timestamp: Date.now()
        }));
        
        return true;
      }
    } catch (error) {
      console.warn('無法載入最新數據，嘗試使用快取...');
      return this.loadFromCache();
    }
    return false;
  }

  async loadWeeklyPerformance() {
    try {
      const response = await fetch('website_data/weekly_performance.json?v=' + Date.now());
      this.weeklyPerformance = await response.json();
      console.log('✅ 載入週報數據');
      return true;
    } catch (error) {
      console.warn('無法載入週報數據，使用預設值');
      this.weeklyPerformance = this.getDefaultWeeklyData();
      return false;
    }
  }

  loadFromCache() {
    try {
      const cached = localStorage.getItem('aiStocksData');
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        
        // 檢查是否過期
        if (Date.now() - timestamp < this.cacheDuration) {
          this.todayStocks = data;
          console.log(`📦 使用快取數據: ${data.length} 支`);
          return true;
        }
      }
    } catch (error) {
      console.error('讀取快取失敗:', error);
    }
    
    // 使用示例數據
    this.todayStocks = this.getSampleData();
    console.log('📝 使用示例數據');
    return false;
  }

  renderAll() {
    this.renderStocks();
    this.renderPerformance();
  }

  renderStocks() {
    const tbody = document.getElementById('todayStocksTable');
    if (!tbody) return;
    
    if (this.todayStocks.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 3rem; color: #718096;">
            <i class="fas fa-exclamation-circle fa-2x" style="margin-bottom: 1rem;"></i>
            <p>暫無今日選股數據</p>
            <p style="font-size: 0.9rem;">請稍後再試或檢查更新</p>
          </td>
        </tr>
      `;
      return;
    }
    
    tbody.innerHTML = this.todayStocks.map(stock => {
      const changeClass = stock.changePercent > 0 ? 'positive' : 'negative';
      const changeIcon = stock.changePercent > 0 ? '📈' : '📉';
      
      // 策略標籤
      let tagClass = 'tag-strong';
      if (stock.strategy.includes('超跌反彈')) tagClass = 'tag-rebound';
      if (stock.strategy.includes('量價齊升')) tagClass = 'tag-volume';
      
      // 評分顏色
      let scoreColor = '#48bb78'; // 綠色
      if (stock.aiScore < 60) scoreColor = '#e53e3e'; // 紅色
      else if (stock.aiScore < 80) scoreColor = '#ed8936'; // 橙色
      
      return `
        <tr>
          <td><strong>${stock.code}</strong></td>
          <td>${stock.name}</td>
          <td>RM${stock.price}</td>
          <td class="${changeClass}">
            ${changeIcon} ${stock.change}
          </td>
          <td>
            <span class="strategy-tag ${tagClass}">
              ${stock.strategy}
            </span>
          </td>
          <td>
            <span class="ai-score" style="background: linear-gradient(135deg, ${scoreColor}, ${this.lightenColor(scoreColor, 20)})">
              ${stock.aiScore}/100
            </span>
          </td>
        </tr>
      `;
    }).join('');
  }

  renderPerformance() {
    // 更新週表現卡片
    if (this.weeklyPerformance) {
      const elements = {
        weeklyAvgReturn: this.weeklyPerformance.avgReturn,
        successRate: this.weeklyPerformance.successRate,
        totalStocks: `${this.todayStocks.length}隻`,
        bestReturn: this.weeklyPerformance.bestPerformer?.return || '+0.0%',
        bestStock: this.weeklyPerformance.bestPerformer?.name || '--'
      };
      
      Object.entries(elements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
      });
    }
  }

  updateLastUpdateTime() {
    const updateTimeEl = document.getElementById('updateTime');
    if (updateTimeEl) {
      const now = new Date();
      updateTimeEl.textContent = `最後更新: ${now.toLocaleString('zh-CN')}`;
    }
  }

  setupAutoRefresh() {
    // 每10分鐘自動刷新
    setInterval(() => {
      this.checkForUpdates();
    }, 10 * 60 * 1000);
  }

  async checkForUpdates() {
    console.log('🔄 檢查數據更新...');
    const shouldRefresh = await this.hasNewData();
    
    if (shouldRefresh) {
      console.log('🆕 發現新數據，重新載入...');
      await this.loadAllData();
      this.showUpdateNotification();
    }
  }

  async hasNewData() {
    try {
      const response = await fetch('website_data/ai_stocks_latest.json?check=' + Date.now());
      const data = await response.json();
      
      const cached = localStorage.getItem('aiStocksData');
      if (cached) {
        const cachedData = JSON.parse(cached);
        return data.updateTime !== cachedData.updateTime;
      }
      return true;
    } catch (error) {
      return false;
    }
  }

  async refreshData() {
    const refreshBtn = document.querySelector('.refresh-btn');
    const originalHtml = refreshBtn.innerHTML;
    
    // 顯示載入中
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 更新中...';
    refreshBtn.disabled = true;
    
    try {
      await this.loadAllData();
      this.showNotification('✅ 數據更新成功！', 'success');
    } catch (error) {
      this.showNotification('❌ 更新失敗，請稍後再試', 'error');
    } finally {
      // 恢復按鈕
      setTimeout(() => {
        refreshBtn.innerHTML = originalHtml;
        refreshBtn.disabled = false;
      }, 1000);
    }
  }

  showNotification(message, type = 'info') {
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#e53e3e' : '#4299e1'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
      ">
        <strong>${message}</strong>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒後自動移除
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 3000);
  }

  showUpdateNotification() {
    this.showNotification('🔄 數據已自動更新', 'success');
  }

  showError() {
    const tbody = document.getElementById('todayStocksTable');
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; padding: 3rem; color: #e53e3e;">
            <i class="fas fa-exclamation-triangle fa-2x" style="margin-bottom: 1rem;"></i>
            <p>無法載入股票數據</p>
            <p style="font-size: 0.9rem;">請檢查網絡連接或稍後再試</p>
            <button onclick="stockDataManager.refreshData()" 
                    style="margin-top: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
              <i class="fas fa-redo"></i> 重試
            </button>
          </td>
        </tr>
      `;
    }
  }

  // 工具函數
  lightenColor(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    
    return '#' + (
      0x1000000 +
      (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
      (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
      (B < 255 ? B < 1 ? 0 : B : 255)
    ).toString(16).slice(1);
  }

  getDefaultWeeklyData() {
    return {
      avgReturn: '+8.2%',
      successRate: '72%',
      bestPerformer: {
        code: '3182',
        name: 'GENTING',
        return: '+4.5%'
      }
    };
  }

  getSampleData() {
    return [
      { code: '0652NP', name: 'HSI-PWNP', price: '0.572', change: '+2.69%', changePercent: 2.69, strategy: '強勢股', aiScore: 85 },
      { code: '4863', name: 'TELEKOM', price: '6.445', change: '+2.58%', changePercent: 2.58, strategy: '強勢股', aiScore: 82 },
      { code: '3182', name: 'GENTING', price: '4.876', change: '+2.48%', changePercent: 2.48, strategy: '強勢股', aiScore: 78 },
      { code: '1295', name: 'PUBLICBANK', price: '4.208', change: '-2.82%', changePercent: -2.82, strategy: '超跌反彈', aiScore: 88 },
      { code: '5326', name: '99SMART', price: '3.167', change: '-1.71%', changePercent: -1.71, strategy: '超跌反彈', aiScore: 76 },
      { code: '5398', name: 'GAMUDA', price: '4.926', change: '-1.40%', changePercent: -1.4, strategy: '超跌反彈', aiScore: 74 },
      { code: '1155', name: 'MAYBANK', price: '9.286', change: '-1.09%', changePercent: -1.09, strategy: '量價齊升', aiScore: 81 }
    ];
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  window.stockDataManager = new StockDataManager();
});
