# 进入你的项目目录
cd ~/storage/shared/Download/bursasearch/myx_shop

# 创建本地激活系统（不需要 Google Apps Script）
cat > js/activation-local.js << 'EOF'
/**
 * Myx Shop 本地激活系统
 * 用于 localhost 环境测试
 */

class LocalActivationSystem {
    constructor() {
        this.storageKey = 'myx_local_activation';
        this.initialize();
    }
    
    initialize() {
        // 检查URL参数
        this.checkUrlParams();
        
        // 页面加载时更新状态
        document.addEventListener('DOMContentLoaded', () => {
            this.updateStatusDisplay();
            this.setupEventListeners();
        });
    }
    
    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // 测试激活参数
        if (urlParams.has('test_activate')) {
            const code = urlParams.get('test_activate');
            this.testActivate(code);
        }
        
        // 开发者模式
        if (urlParams.has('dev') || urlParams.has('test')) {
            this.activateDeveloperMode();
        }
    }
    
    // 测试激活（用于本地测试）
    testActivate(code) {
        const testCodes = {
            'MYX123456': { days: 30, name: '测试用户1' },
            'MYX789012': { days: 7, name: '测试用户2' },
            'MYX345678': { days: 365, name: '测试用户3' },
            'DEV123456': { days: 9999, name: '开发者' }
        };
        
        if (testCodes[code]) {
            const data = testCodes[code];
            this.activateLocal(code, data.days, data.name);
            alert(`✅ 测试激活成功！\n激活码: ${code}\n有效期: ${data.days}天\n用户: ${data.name}`);
        }
    }
    
    // 本地激活
    activateLocal(code, days = 30, customerName = '') {
        const activation = {
            code: code,
            status: 'activated',
            customerName: customerName,
            days: days,
            activatedAt: new Date().toISOString(),
            expiryDate: this.calculateExpiryDate(days)
        };
        
        // 保存到 localStorage
        localStorage.setItem(this.storageKey, JSON.stringify(activation));
        
        // 设置会员状态
        localStorage.setItem('myx_member', 'true');
        localStorage.setItem('myx_expiry', activation.expiryDate);
        localStorage.setItem('myx_customer_name', customerName);
        
        // 同步到其他系统
        localStorage.setItem('bursa_premium', 'true');
        localStorage.setItem('bursa_expiry', activation.expiryDate);
        
        console.log('本地激活成功:', activation);
        
        // 更新显示
        this.updateStatusDisplay();
        
        return activation;
    }
    
    // 激活开发者模式
    activateDeveloperMode() {
        const expiry = new Date();
        expiry.setFullYear(expiry.getFullYear() + 10); // 10年
        
        localStorage.setItem('dev_access', 'true');
        localStorage.setItem('dev_expiry', expiry.toISOString());
        localStorage.setItem('myx_member', 'true');
        localStorage.setItem('myx_expiry', expiry.toISOString());
        localStorage.setItem('bursa_premium', 'true');
        localStorage.setItem('bursa_expiry', expiry.toISOString());
        
        console.log('开发者模式已激活');
    }
    
    // 计算过期时间
    calculateExpiryDate(days) {
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString();
    }
    
    // 获取激活状态
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
                    message: '已过期',
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
    
    // 显示激活模态框
    showActivationModal() {
        const modalHtml = `
            <div id="localActivationModal" style="
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
                            🧪 本地激活测试 (localhost)
                        </h3>
                        <button onclick="localActivation.hideModal()" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #666;
                        ">×</button>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <p style="color: #666;">
                            这是本地测试环境，请输入测试激活码：
                        </p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold;">
                            测试激活码
                        </label>
                        <select id="testCodeSelect" style="
                            width: 100%;
                            padding: 12px;
                            border: 2px solid #ddd;
                            border-radius: 5px;
                            font-size: 16px;
                            margin-bottom: 10px;
                        ">
                            <option value="MYX123456">MYX123456 - 30天测试</option>
                            <option value="MYX789012">MYX789012 - 7天测试</option>
                            <option value="MYX345678">MYX345678 - 1年测试</option>
                            <option value="DEV123456">DEV123456 - 开发者模式</option>
                        </select>
                        
                        <input type="text" id="customCodeInput" 
                            placeholder="或输入自定义激活码"
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
                    </div>
                    
                    <div style="margin-bottom: 25px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold;">
                            姓名 (可选)
                        </label>
                        <input type="text" id="customerNameInput" 
                            placeholder="输入您的姓名"
                            style="
                                width: 100%;
                                padding: 12px;
                                border: 2px solid #ddd;
                                border-radius: 5px;
                                font-size: 16px;
                            "
                        >
                    </div>
                    
                    <div style="margin-bottom: 25px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold;">
                            有效期 (天)
                        </label>
                        <select id="daysSelect" style="
                            width: 100%;
                            padding: 12px;
                            border: 2px solid #ddd;
                            border-radius: 5px;
                            font-size: 16px;
                        ">
                            <option value="7">7天</option>
                            <option value="30" selected>30天</option>
                            <option value="90">90天</option>
                            <option value="365">1年</option>
                            <option value="9999">永久</option>
                        </select>
                    </div>
                    
                    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                        <button onclick="localActivation.processLocalActivation()" style="
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
                            🧪 测试激活
                        </button>
                        <button onclick="localActivation.hideModal()" style="
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
                            💡 本地测试说明
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #666;">
                            <li>这是本地测试环境，数据保存在浏览器中</li>
                            <li>实际使用时需要连接 Google Apps Script</li>
                            <li>测试激活码：MYX123456, MYX789012, MYX345678</li>
                            <li>开发者模式：DEV123456</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 20px; text-align: center;">
                        <button onclick="localActivation.clearActivation()" style="
                            background: #f44336;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-size: 14px;
                            cursor: pointer;
                        ">
                            清除激活状态
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // 移除现有的模态框
        this.hideModal();
        
        // 添加新的模态框
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    // 隐藏模态框
    hideModal() {
        const modal = document.getElementById('localActivationModal');
        if (modal) modal.remove();
    }
    
    // 处理本地激活
    processLocalActivation() {
        const select = document.getElementById('testCodeSelect');
        const customInput = document.getElementById('customCodeInput');
        const nameInput = document.getElementById('customerNameInput');
        const daysSelect = document.getElementById('daysSelect');
        
        let code = customInput.value.trim();
        if (!code && select) {
            code = select.value;
        }
        
        if (!code) {
            alert('请输入激活码');
            return;
        }
        
        const customerName = nameInput ? nameInput.value.trim() : '';
        const days = daysSelect ? parseInt(daysSelect.value) : 30;
        
        // 显示加载状态
        const button = document.querySelector('#localActivationModal button[onclick*="processLocalActivation"]');
        const originalText = button.textContent;
        button.textContent = '激活中...';
        button.disabled = true;
        
        setTimeout(() => {
            try {
                const activation = this.activateLocal(code, days, customerName);
                
                // 显示成功消息
                alert(`✅ 本地激活成功！\n\n激活码: ${code}\n有效期: ${days}天\n用户: ${customerName || '匿名用户'}`);
                
                // 关闭模态框
                this.hideModal();
                
                // 刷新页面
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } catch (error) {
                alert('激活失败：' + error.message);
            } finally {
                // 恢复按钮
                button.textContent = originalText;
                button.disabled = false;
            }
        }, 500);
    }
    
    // 清除激活状态
    clearActivation() {
        if (confirm('确定要清除所有激活状态吗？')) {
            localStorage.removeItem(this.storageKey);
            localStorage.removeItem('myx_member');
            localStorage.removeItem('myx_expiry');
            localStorage.removeItem('myx_customer_name');
            localStorage.removeItem('bursa_premium');
            localStorage.removeItem('bursa_expiry');
            
            alert('✅ 激活状态已清除');
            this.hideModal();
            this.updateStatusDisplay();
        }
    }
    
    // 设置事件监听器
    setupEventListeners() {
        // 为所有需要激活的功能添加点击事件
        const premiumElements = document.querySelectorAll('.premium-only, [data-requires-activation]');
        
        premiumElements.forEach(element => {
            element.addEventListener('click', (e) => {
                const status = this.getActivationStatus();
                
                if (!status.active) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // 显示激活模态框
                    this.showActivationModal();
                    
                    // 滚动到顶部
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }
    
    // 更新状态显示
    updateStatusDisplay() {
        const status = this.getActivationStatus();
        
        // 更新激活状态元素
        const statusElement = document.getElementById('activationStatus');
        if (statusElement) {
            if (status.active) {
                statusElement.innerHTML = \`
                    <div style="color: #4CAF50; font-weight: bold; font-size: 18px;">
                        ✅ 已激活 (本地测试)
                    </div>
                    <div style="font-size: 14px; color: #666; margin-top: 5px;">
                        剩余 \${status.daysLeft} 天 | 激活码: \${status.code}
                    </div>
                    \${status.customerName ? \`
                    <div style="font-size: 14px; color: #666; margin-top: 5px;">
                        用户: \${status.customerName}
                    </div>
                    \` : ''}
                \`;
                
                // 显示容器
                const container = document.getElementById('activationStatusContainer');
                if (container) {
                    container.style.display = 'block';
                    container.style.background = '#e8f5e9';
                    container.style.borderColor = '#4CAF50';
                }
                
                // 解锁付费功能
                this.unlockPremiumFeatures();
            } else {
                statusElement.innerHTML = \`
                    <div style="color: #f44336; font-weight: bold; font-size: 18px;">
                        ❌ 未激活
                    </div>
                    <div style="font-size: 14px; color: #666; margin-top: 5px;">
                        点击下方按钮进行本地测试激活
                    </div>
                \`;
                
                // 显示激活按钮
                this.showActivationButton();
            }
        }
        
        // 更新会员状态
        const memberStatus = document.getElementById('memberStatus');
        if (memberStatus) {
            memberStatus.textContent = status.active ? '高级会员 (本地测试)' : '免费用户';
            memberStatus.style.color = status.active ? '#4CAF50' : '#f44336';
        }
    }
    
    // 显示激活按钮
    showActivationButton() {
        // 如果已经有激活按钮，不需要重复添加
        if (document.getElementById('localActivationBtn')) {
            return;
        }
        
        const buttonHtml = \`
            <div style="text-align: center; margin: 20px 0;">
                <button id="localActivationBtn" 
                        onclick="localActivation.showActivationModal()"
                        style="
                            background: linear-gradient(135deg, #2196F3, #1976D2);
                            color: white;
                            border: none;
                            padding: 15px 30px;
                            border-radius: 8px;
                            font-size: 18px;
                            font-weight: bold;
                            cursor: pointer;
                            box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
                            transition: all 0.3s;
                        "
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(33, 150, 243, 0.4)';"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 10px rgba(33, 150, 243, 0.3)';">
                    🧪 本地测试激活
                </button>
                <p style="margin-top: 10px; color: #666; font-size: 14px;">
                    点击进行本地测试激活 (localhost:5050)
                </p>
            </div>
        \`;
        
        // 插入到合适的位置，例如在支付区域之前
        const paymentSection = document.getElementById('paymentSection');
        if (paymentSection) {
            paymentSection.insertAdjacentHTML('beforebegin', buttonHtml);
        } else {
            document.body.insertAdjacentHTML('beforeend', buttonHtml);
        }
    }
    
    // 解锁付费功能
    unlockPremiumFeatures() {
        // 移除锁定样式
        const lockedElements = document.querySelectorAll('.premium-only, .locked, [data-requires-activation]');
        lockedElements.forEach(el => {
            el.classList.remove('premium-only', 'locked');
            el.style.opacity = '1';
            el.style.filter = 'none';
            el.style.pointerEvents = 'auto';
            el.style.cursor = 'pointer';
            
            // 移除点击事件监听器
            const newEl = el.cloneNode(true);
            el.parentNode.replaceChild(newEl, el);
        });
        
        // 隐藏支付区域
        const paymentSection = document.getElementById('paymentSection');
        if (paymentSection) {
            paymentSection.style.display = 'none';
        }
        
        // 显示激活状态区域
        const accessStatus = document.getElementById('accessStatus');
        if (accessStatus) {
            accessStatus.style.display = 'block';
        }
    }
}

// 创建全局实例
window.localActivation = new LocalActivationSystem();
EOF
