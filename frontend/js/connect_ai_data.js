// connect_ai_data.js - 連接AI分析結果

class AIDataConnector {
  constructor() {
    this.aiData = null;
    this.init();
  }

  async init() {
    // 1. 從本地JSON加載AI分析結果
    await this.loadAIData();
    
    // 2. 更新股票推薦區塊
    this.updateStockCards();
    
    // 3. 設置定時更新
    this.setupAutoRefresh();
  }

  async loadAIData() {
    try {
      // 從picks.json加載數據
      const response = await fetch('picks.json');
      this.aiData = await response.json();
      
      console.log('✅ AI數據加載成功:', this.aiData);
      return this.aiData;
    } catch (error) {
      console.error('❌ 加載AI數據失敗:', error);
      return this.getFallbackData();
    }
  }

  updateStockCards() {
    if (!this.aiData || !this.aiData.picks) return;
    
    const picks = this.aiData.picks;
    const stockGrid = document.querySelector('.stock-grid');
    
    if (!stockGrid) return;
    
    // 更新股票卡片（使用前3個推薦）
    const topPicks = picks.slice(0, 3);
    const stockCards = stockGrid.querySelectorAll('.stock-card');
    
    topPicks.forEach((pick, index) => {
      if (stockCards[index]) {
        this.updateStockCard(stockCards[index], pick);
      }
    });
    
    // 更新頁面標題中的時間
    this.updatePageHeader();
  }

  updateStockCard(cardElement, pick) {
    const sector = pick.sector || '未知';
    const performance = pick.change_5d || '+0.0%';
    const score = pick.score || 0;
    
    // 根據行業設置標題
    const sectorIcons = {
      'Technology': 'microchip',
      'Finance': 'university',
      'Industrial': 'industry',
      'Consumer': 'shopping-cart',
      'Energy': 'bolt',
      'Healthcare': 'heartbeat',
      'Property': 'building',
      'Plantation': 'leaf'
    };
    
    const icon = sectorIcons[sector] || 'chart-line';
    
    // 風險等級判斷
    let riskLevel = 'risk-medium';
    let riskText = '中';
    if (score >= 85) {
      riskLevel = 'risk-low';
      riskText = '低';
    } else if (score <= 60) {
      riskLevel = 'risk-high';
      riskText = '高';
    }
    
    cardElement.innerHTML = `
      <h3><i class="fas fa-${icon}"></i> ${sector}推薦</h3>
      <p>股票: <strong>${pick.code} ${pick.name}</strong></p>
      <p>近期表現: <span class="performance">${performance}</span></p>
      <p>風險等級: <span class="${riskLevel}">${riskText}</span></p>
      <p>AI評分: <span class="ai-score">${score}/100</span></p>
      <p>建議: <strong>${pick.recommendation}</strong></p>
    `;
  }

  updatePageHeader() {
    const header = document.querySelector('.page-header p');
    if (header && this.aiData) {
      const date = new Date(this.aiData.last_updated).toLocaleDateString('zh-Hans-CN');
      header.textContent = `基於人工智能算法的股票分析與推薦 - 最後更新: ${date}`;
    }
  }

  getFallbackData() {
    return {
      picks: [
        {
          code: 'TECH001',
          name: '示例科技股',
          sector: 'Technology',
          score: 88,
          change_5d: '+15.2%',
          recommendation: '買入'
        },
        {
          code: 'FIN001',
          name: '示例金融股',
          sector: 'Finance',
          score: 92,
          change_5d: '+8.7%',
          recommendation: '強力買入'
        },
        {
          code: 'ENE001',
          name: '示例能源股',
          sector: 'Energy',
          score: 76,
          change_5d: '+22.1%',
          recommendation: '觀望'
        }
      ],
      last_updated: new Date().toISOString()
    };
  }

  setupAutoRefresh() {
    // 每小時檢查一次更新
    setInterval(async () => {
      console.log('🔄 檢查AI數據更新...');
      await this.loadAIData();
      this.updateStockCards();
    }, 60 * 60 * 1000); // 1小時
  }
}

// 導出供其他腳本使用
window.AIDataConnector = AIDataConnector;
