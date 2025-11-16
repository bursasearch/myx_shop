// js/auto_update_stocks.js - 自动股票数据更新
class AutoUpdateStocks {
    constructor() {
        this.config = {
            updateInterval: 30 * 60 * 1000, // 30分钟
            apiEndpoint: 'https://your-api-endpoint.com/stocks', // 替换为您的API
            fallbackData: this.getFallbackData()
        };
        this.init();
    }

    async init() {
        await this.loadInitialData();
        this.startAutoUpdate();
        this.setupRealTimeUpdates();
    }

    async loadInitialData() {
        // 尝试从API获取数据，失败则使用本地存储或默认数据
        try {
            const data = await this.fetchFromAPI();
            this.updateDisplay(data);
        } catch (error) {
            console.warn('API请求失败，使用缓存数据:', error);
            this.useCachedData();
        }
    }

    async fetchFromAPI() {
        // 替换为您的实际API调用
        const response = await fetch(this.config.apiEndpoint);
        if (!response.ok) throw new Error('API请求失败');
        return await response.json();
    }

    useCachedData() {
        const cached = localStorage.getItem('stockData');
        if (cached) {
            this.updateDisplay(JSON.parse(cached));
        } else {
            this.updateDisplay(this.config.fallbackData);
        }
    }

    updateDisplay(data) {
        // 更新股票卡片
        this.updateStockCards(data);
        
        // 更新视频内容（如果需要）
        this.updateVideoContent(data);
        
        // 保存数据
        this.saveData(data);
    }

    updateStockCards(data) {
        const cards = document.querySelectorAll('.stock-card');
        
        cards.forEach((card, index) => {
            const performance = card.querySelector('.performance');
            const riskSpan = card.querySelector('[class*="risk-"]');
            const scoreText = card.querySelector('p:last-child');
            
            if (index === 0 && data.tech) {
                performance.textContent = data.tech.performance;
                riskSpan.textContent = data.tech.risk;
                riskSpan.className = `risk-${this.getRiskClass(data.tech.risk)}`;
                scoreText.textContent = `AI評分: ${data.tech.score}`;
            } else if (index === 1 && data.finance) {
                performance.textContent = data.finance.performance;
                riskSpan.textContent = data.finance.risk;
                riskSpan.className = `risk-${this.getRiskClass(data.finance.risk)}`;
                scoreText.textContent = `AI評分: ${data.finance.score}`;
            } else if (index === 2 && data.energy) {
                performance.textContent = data.energy.performance;
                riskSpan.textContent = data.energy.risk;
                riskSpan.className = `risk-${this.getRiskClass(data.energy.risk)}`;
                scoreText.textContent = `AI評分: ${data.energy.score}`;
            }
        });
    }

    updateVideoContent(data) {
        if (data.latestVideo) {
            const videoBlock = document.querySelector('.video-block');
            if (videoBlock && data.latestVideo.id) {
                videoBlock.id = `video-${data.latestVideo.id}`;
                videoBlock.querySelector('h3').textContent = data.latestVideo.title;
                videoBlock.querySelector('p').textContent = `更新日期：${data.latestVideo.date}`;
                
                const img = videoBlock.querySelector('img');
                const iframe = videoBlock.querySelector('iframe');
                
                if (img) {
                    img.src = `https://img.youtube.com/vi/${data.latestVideo.id}/maxresdefault.jpg`;
                    img.onerror = function() {
                        this.src = `https://img.youtube.com/vi/${data.latestVideo.id}/hqdefault.jpg`;
                    };
                }
                
                if (iframe) {
                    iframe.src = `https://www.youtube.com/embed/${data.latestVideo.id}`;
                }
            }
        }
    }

    startAutoUpdate() {
        setInterval(async () => {
            try {
                const data = await this.fetchFromAPI();
                this.updateDisplay(data);
                console.log('自动更新完成:', new Date().toLocaleString());
            } catch (error) {
                console.error('自动更新失败:', error);
            }
        }, this.config.updateInterval);
    }

    setupRealTimeUpdates() {
        // 如果需要实时更新，可以设置WebSocket连接
        // this.setupWebSocket();
    }

    saveData(data) {
        localStorage.setItem('stockData', JSON.stringify(data));
        localStorage.setItem('lastAutoUpdate', new Date().toISOString());
    }

    getRiskClass(risk) {
        const riskMap = {
            '低': 'low',
            '中': 'medium',
            '高': 'high'
        };
        return riskMap[risk] || 'medium';
    }

    getFallbackData() {
        return {
            tech: { performance: '+15.2%', risk: '中', score: '88/100' },
            finance: { performance: '+8.7%', risk: '低', score: '92/100' },
            energy: { performance: '+22.1%', risk: '高', score: '76/100' },
            latestVideo: {
                id: 'AxlIA-OivOs',
                title: '【Ai選股】最新AI選股分析報告',
                date: new Date().toLocaleDateString('zh-Hans-CN')
            }
        };
    }
}

// 初始化自动更新
document.addEventListener('DOMContentLoaded', function() {
    console.log('自动股票更新脚本加载完成');
    new AutoUpdateStocks();
});
