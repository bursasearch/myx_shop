// js/update_stocks.js - 股票数据更新脚本
class StockUpdater {
    constructor() {
        this.lastUpdate = localStorage.getItem('lastStockUpdate') || new Date().toLocaleDateString();
        this.updateButton = null;
        this.init();
    }

    init() {
        this.createUpdateButton();
        this.loadStockData();
        this.setupAutoRefresh();
        this.addStyles();
    }

    createUpdateButton() {
        this.updateButton = document.createElement('button');
        this.updateButton.innerHTML = '<i class="fas fa-sync-alt"></i> 立即更新股票数据';
        this.updateButton.className = 'nav-btn';
        this.updateButton.style.marginLeft = 'auto';
        this.updateButton.onclick = () => this.manualUpdate();
        
        const navButtons = document.querySelector('.nav-buttons');
        if (navButtons) {
            navButtons.appendChild(this.updateButton);
        }
    }

    async manualUpdate() {
        this.updateButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 更新中...';
        this.updateButton.disabled = true;

        try {
            await this.fetchLatestData();
            this.showSuccessMessage('数据更新成功！');
        } catch (error) {
            this.showErrorMessage('更新失败，请重试');
            console.error('Update error:', error);
        } finally {
            this.updateButton.innerHTML = '<i class="fas fa-sync-alt"></i> 立即更新股票数据';
            this.updateButton.disabled = false;
        }
    }

    async fetchLatestData() {
        // 模拟API调用 - 替换为您的实际数据源
        return new Promise((resolve) => {
            setTimeout(() => {
                const mockData = {
                    tech: {
                        performance: this.generateRandomPerformance(10, 20),
                        risk: '中',
                        score: this.generateRandomScore(85, 95)
                    },
                    finance: {
                        performance: this.generateRandomPerformance(5, 12),
                        risk: '低',
                        score: this.generateRandomScore(90, 98)
                    },
                    energy: {
                        performance: this.generateRandomPerformance(15, 25),
                        risk: '高',
                        score: this.generateRandomScore(70, 85)
                    },
                    latestVideo: this.getLatestVideoInfo()
                };

                this.updateStockCards(mockData);
                this.updateVideoContent(mockData);
                this.updateLastModified();
                
                localStorage.setItem('stockData', JSON.stringify(mockData));
                localStorage.setItem('lastStockUpdate', new Date().toLocaleDateString());
                
                resolve(mockData);
            }, 1500); // 模拟网络延迟
        });
    }

    generateRandomPerformance(min, max) {
        const value = (Math.random() * (max - min) + min).toFixed(1);
        return `+${value}%`;
    }

    generateRandomScore(min, max) {
        const score = Math.floor(Math.random() * (max - min) + min);
        return `${score}/100`;
    }

    getLatestVideoInfo() {
        const videos = [
            { id: 'AxlIA-OivOs', title: '【Ai選股】最新AI選股分析報告', date: new Date().toLocaleDateString('zh-Hans-CN') },
            { id: 'dQw4w9WgXcQ', title: '【Ai選股】技術指標深度解析', date: new Date().toLocaleDateString('zh-Hans-CN') },
            { id: 'abc123def456', title: '【Ai選股】市場趨勢預測', date: new Date().toLocaleDateString('zh-Hans-CN') }
        ];
        return videos[Math.floor(Math.random() * videos.length)];
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
            // 更新现有的视频区块
            const existingVideoBlock = document.querySelector('.video-block');
            if (existingVideoBlock) {
                existingVideoBlock.id = `video-${data.latestVideo.id}`;
                existingVideoBlock.querySelector('h3').textContent = data.latestVideo.title;
                existingVideoBlock.querySelector('p').textContent = `更新日期：${data.latestVideo.date}`;
                
                const img = existingVideoBlock.querySelector('img');
                const iframe = existingVideoBlock.querySelector('iframe');
                const link = existingVideoBlock.querySelector('a');
                
                if (img) {
                    img.src = `https://img.youtube.com/vi/${data.latestVideo.id}/maxresdefault.jpg`;
                    img.alt = data.latestVideo.title;
                }
                
                if (iframe) {
                    iframe.src = `https://www.youtube.com/embed/${data.latestVideo.id}`;
                    iframe.title = data.latestVideo.title;
                }
                
                if (link) {
                    link.href = `https://www.youtube.com/watch?v=${data.latestVideo.id}`;
                }
            }
        }
    }

    getRiskClass(risk) {
        const riskMap = {
            '低': 'low',
            '中': 'medium',
            '高': 'high'
        };
        return riskMap[risk] || 'medium';
    }

    updateLastModified() {
        const updateElements = document.querySelectorAll('.update-time');
        const now = new Date();
        const timeString = `${now.toLocaleDateString("zh-Hans-CN")} ${now.toLocaleTimeString("zh-Hans-CN", {hour: '2-digit', minute: '2-digit'})}`;
        
        updateElements.forEach(element => {
            element.innerHTML = `最後更新: ${timeString}`;
        });
    }

    loadStockData() {
        const savedData = localStorage.getItem('stockData');
        if (savedData) {
            const data = JSON.parse(savedData);
            this.updateStockCards(data);
            
            // 显示最后更新时间
            const lastUpdate = localStorage.getItem('lastStockUpdate');
            if (lastUpdate) {
                const updateElements = document.querySelectorAll('.update-time');
                updateElements.forEach(element => {
                    element.innerHTML = `最後更新: ${lastUpdate}`;
                });
            }
        }
    }

    setupAutoRefresh() {
        // 每30分钟自动检查更新
        setInterval(() => {
            this.checkForUpdates();
        }, 30 * 60 * 1000);
    }

    async checkForUpdates() {
        console.log('自动检查数据更新...', new Date().toLocaleString());
        // 这里可以添加实际的更新检查逻辑
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 2rem;
            background: ${type === 'success' ? '#48bb78' : '#e53e3e'};
            color: white;
            border-radius: 10px;
            z-index: 1000;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }

    addStyles() {
        if (document.querySelector('#stock-updater-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'stock-updater-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .nav-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .fa-spin {
                animation: fa-spin 1s infinite linear;
            }
            
            @keyframes fa-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

// 初始化更新器
document.addEventListener('DOMContentLoaded', function() {
    console.log('股票更新脚本加载完成');
    new StockUpdater();
});
