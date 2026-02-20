# 回到項目目錄
cd ~/storage/shared/Download/bursasearch/myx_shop

# 創建簡化版的激活系統
cat > js/activation-simple.js << 'EOF'
/**
 * Myx Shop 簡化版激活系統
 * 使用 Google Apps Script API
 */

class ActivationSystem {
    constructor() {
        this.apiUrl = ''; // 將在頁面中設置
        this.storageKey = 'myx_activation';
        this.initialize();
    }
    
    initialize() {
        // 嘗試從 localStorage 加載配置
        const config = this.loadConfig();
        if (config.apiUrl) {
            this.apiUrl = config.apiUrl;
        }
        
        // 頁面加載時更新狀態
        document.addEventListener('DOMContentLoaded', () => {
            this.updateStatusDisplay();
        });
    }
    
    loadConfig() {
        try {
            const config = localStorage.getItem(this.storageKey + '_config');
            return config ? JSON.parse(config) : {};
        } catch (e) {
            return {};
        }
    }
    
    saveConfig(config) {
        localStorage.setItem(this.storageKey + '_config', JSON.stringify(config));
    }
    
    // 設置 API URL
    setApiUrl(url) {
        this.apiUrl = url;
        this.saveConfig({ apiUrl: url });
        console.log('API URL 已設置:', url);
    }
    
    // 驗證激活碼
    async validateCode(code) {
        if (!this.apiUrl) {
            return {
                success: false,
                message: '請先設置 API URL',
                showSetup: true
            };
        }
        
        if (!code || !code.trim()) {
            return {
                success: false,
                message: '請輸入激活碼'
            };
        }
        
        // 格式化激活碼
        code = code.trim().toUpperCase();
        
        // 檢查格式
        if (!code.match(/^MYX\d{6}$/)) {
            return {
                success: false,
                message: '激活碼格式不正確，應為 MYX 開頭加上6位數字（例如：MYX123456）'
            };
        }
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'validate',
                    code: code
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 激活成功，保存信息
                this.saveActivation(data.data);
                return data;
            } else {
                return data;
            }
        } catch (error) {
            console.error('驗證失敗:', error);
            return {
                success: false,
                message: '網絡錯誤，請檢查 API URL 和網絡連接'
            };
        }
    }
    
    // 保存激活信息
    saveActivation(data) {
        const activation = {
            code: data.code,
            status: data.status,
            customerName: data.customerName || '',
            days: data.days || 30,
            orderId: data.orderId || '',
            activatedAt: new Date().toISOString(),
            expiryDate: this.calculateExpiryDate(data.days || 30)
        };
        
        // 保存到 localStorage
        localStorage.setItem(this.storageKey, JSON.stringify(activation));
        
        // 同時設置會員狀態
        localStorage.setItem('myx_member', 'true');
        localStorage.setItem('myx_expiry', activation.expiryDate);
        localStorage.setItem('myx_customer_name', activation.customerName);
        
        // 同步到其他系統
        localStorage.setItem('bursa_premium', 'true');
        localStorage.setItem('bursa_expiry', activation.expiryDate);
        
        console.log('激活信息已保存:', activation);
    }
    
    // 計算過期時間
    calculateExpiryDate(days) {
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString();
    }
    
    // 獲取激活狀態
    getActivationStatus() {
        try {
            const activation = localStorage.getItem(this.storageKey);
            if (!activation) {
                return { active: false, message: '未激活' };
            }
            
            const data = JSON.parse(activation);
            const expiry = new Date(data.expiryDate);
            const now = new Date();
            
            if (now > expiry) {
                return { 
                    active: false, 
                    message: '已過期',
                    expired: true,
                    expiryDate: expiry
                };
            }
            
            const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
            
            return {
                active: true,
                message: '已激活',
                daysLeft: daysLeft,
                expiryDate: expiry,
                customerName: data.customerName,
                code: data.code
            };
        } catch (e) {
            return { active: false, message: '未激活' };
        }
    }
    
    // 顯示激活模態框
    showActivationModal() {
        // 如果沒有 API URL，先顯示設置對話框
        if (!this.apiUrl) {
            this.showSetupDialog();
            return;
        }
        
        const modalHtml = `
            <div id="activationModal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            ">
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 90vh;
                    overflow-y: auto;
                ">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 20px;
                    ">
                        <h3 style="margin: 0; color: #2196F3;">
                            🔑 激活 Myx Shop
                        </h3>
                        <button onclick="activationSystem.hideModal()" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #666;
                        ">×</button>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold;">
                            激活碼
                        </label>
                        <input type="text" id="activationCodeInput" 
                            placeholder="輸入 MYX 開頭的激活碼 (如: MYX123456)"
                            style="
                                width: 100%;
                                padding: 12px;
                                border: 2px solid #ddd;
                                border-radius: 5px;
                                font-size: 16px;
                                text-transform: uppercase;
                            "
                            oninput="this.value = this.value.toUpperCase()"
                        >
                        <small style="color: #666; display: block; margin-top: 5px;">
                            格式：MYX + 6位數字 (例如：MYX123456)
                        </small>
                    </div>
                    
                    <div style="margin-bottom: 25px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold;">
                            姓名 (可選)
                        </label>
                        <input type="text" id="customerNameInput" 
                            placeholder="輸入您的姓名"
                            style="
                                width: 100%;
                                padding: 12px;
                                border: 2px solid #ddd;
                                border-radius: 5px;
                                font-size: 16px;
                            "
                        >
                    </div>
                    
                    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                        <button onclick="activationSystem.processActivation()" style="
                            flex: 2;
                            background: linear-gradient(135deg, #4CAF50, #388E3C);
                            color: white;
                            border: none;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                        ">
                            🔓 激活賬戶
                        </button>
                        <button onclick="activationSystem.hideModal()" style="
                            flex: 1;
                            background: #f5f5f5;
                            color: #333;
                            border: 1px solid #ddd;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: 16px;
                            cursor: pointer;
                        ">
                            取消
                        </button>
                    </div>
                    
                    <div style="
                        background: #f9f9f9;
                        padding: 15px;
                        border-radius: 5px;
                        border-left: 4px solid #2196F3;
                    ">
                        <p style="margin: 0 0 10px 0; font-weight: bold; color: #333;">
                            💡 如何獲取激活碼？
                        </p>
                        <ol style="margin: 0; padding-left: 20px; color: #666;">
                            <li>聯繫客服購買 Myx Shop 服務</li>
                            <li>您將收到包含激活碼的郵件</li>
                            <li>輸入激活碼解鎖全部功能</li>
                        </ol>
                    </div>
                </div>
            </div>
        `;
        
        // 移除現有的模態框
        this.hideModal();
        
        // 添加新的模態框
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    // 顯示設置對話框
    showSetupDialog() {
        const dialogHtml = `
            <div id="setupDialog" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            ">
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 500px;
                    width: 90%;
                ">
                    <h3 style="margin: 0 0 20px 0; color: #2196F3;">
                        🔧 設置激活 API
                    </h3>
                    
                    <p style="margin-bottom: 20px;">
                        請輸入您的 Google Apps Script Web App URL：
                    </p>
                    
                    <div style="margin-bottom: 20px;">
                        <input type="text" id="apiUrlInput" 
                            placeholder="https://script.google.com/macros/s/.../exec"
                            style="
                                width: 100%;
                                padding: 12px;
                                border: 2px solid #ddd;
                                border-radius: 5px;
                                font-size: 16px;
                            "
                        >
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button onclick="activationSystem.saveApiUrl()" style="
                            flex: 1;
                            background: linear-gradient(135deg, #2196F3, #1976D2);
                            color: white;
                            border: none;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                        ">
                            保存
                        </button>
                        <button onclick="activationSystem.hideModal()" style="
                            flex: 1;
                            background: #f5f5f5;
                            color: #333;
                            border: 1px solid #ddd;
                            padding: 15px;
                            border-radius: 5px;
                            font-size: 16px;
                            cursor: pointer;
                        ">
                            取消
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialogHtml);
    }
    
    // 保存 API URL
    saveApiUrl() {
        const input = document.getElementById('apiUrlInput');
        if (input && input.value) {
            this.setApiUrl(input.value.trim());
            this.hideModal();
            // 重新顯示激活模態框
            setTimeout(() => this.showActivationModal(), 300);
        }
    }
    
    // 隱藏模態框
    hideModal() {
        const modal = document.getElementById('activationModal');
        if (modal) modal.remove();
        
        const dialog = document.getElementById('setupDialog');
        if (dialog) dialog.remove();
    }
    
    // 處理激活
    async processActivation() {
        const codeInput = document.getElementById('activationCodeInput');
        const nameInput = document.getElementById('customerNameInput');
        
        if (!codeInput || !codeInput.value.trim()) {
            alert('請輸入激活碼');
            return;
        }
        
        const code = codeInput.value.trim();
        const customerName = nameInput ? nameInput.value.trim() : '';
        
        // 顯示加載狀態
        const button = document.querySelector('#activationModal button[onclick*="processActivation"]');
        const originalText = button.textContent;
        button.textContent = '驗證中...';
        button.disabled = true;
        
        try {
            const result = await this.validateCode(code);
            
            if (result.success) {
                // 如果用戶輸入了姓名，更新存儲
                if (customerName) {
                    const activation = JSON.parse(localStorage.getItem(this.storageKey) || '{}');
                    activation.customerName = customerName;
                    localStorage.setItem(this.storageKey, JSON.stringify(activation));
                    localStorage.setItem('myx_customer_name', customerName);
                }
                
                // 顯示成功消息
                alert(`✅ 激活成功！\n\n您的賬戶已激活，有效期 ${result.data.days} 天`);
                
                // 關閉模態框
                this.hideModal();
                
                // 更新顯示
                this.updateStatusDisplay();
                
                // 刷新頁面
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                alert('激活失敗：' + result.message);
                
                // 如果需要設置 API URL
                if (result.showSetup) {
                    this.hideModal();
                    this.showSetupDialog();
                }
            }
        } catch (error) {
            alert('激活過程出錯：' + error.message);
        } finally {
            // 恢復按鈕
            button.textContent = originalText;
            button.disabled = false;
        }
    }
    
    // 更新狀態顯示
    updateStatusDisplay() {
        const status = this.getActivationStatus();
        
        // 更新激活狀態元素
        const statusElement = document.getElementById('activationStatus');
        if (statusElement) {
            if (status.active) {
                statusElement.innerHTML = \`
                    <div style="color: #4CAF50; font-weight: bold;">
                        ✅ 已激活
                    </div>
                    <div style="font-size: 14px; color: #666; margin-top: 5px;">
                        剩餘 \${status.daysLeft} 天
                    </div>
                \`;
                
                // 顯示容器
                const container = document.getElementById('activationStatusContainer');
                if (container) {
                    container.style.display = 'block';
                }
            } else {
                statusElement.innerHTML = \`
                    <div style="color: #f44336; font-weight: bold;">
                        ❌ 未激活
                    </div>
                \`;
            }
        }
        
        // 更新會員狀態
        if (status.active) {
            document.body.classList.add('activated');
            document.body.classList.remove('not-activated');
        } else {
            document.body.classList.add('not-activated');
            document.body.classList.remove('activated');
        }
    }
}

// 創建全局實例
window.activationSystem = new ActivationSystem();
EOF
