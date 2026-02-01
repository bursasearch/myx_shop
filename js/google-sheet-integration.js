// myx_shop/js/google-sheet-integration.js
// Google Sheet 配置 - 請替換為您的實際ID
const GOOGLE_CONFIG = {
    // 您的 Apps Script Web App URL
    scriptUrl: 'https://script.google.com/macros/s/YOUR_APPS_SCRIPT_DEPLOYMENT_ID/exec',
    
    // 您的 Google Sheet ID（用於直接訪問鏈接）
    sheetId: 'YOUR_GOOGLE_SHEET_ID'
};

// ============ 雲端密碼系統 ============

// 1. 雲端生成密碼
async function activateCloudMembership() {
    if (typeof showCustomAlert === 'undefined') {
        console.error('showCustomAlert 函數未定義');
        return;
    }
    
    showCustomAlert('<div class="loading">⏳ 正在連接雲端服務...</div>', '請稍候');
    
    try {
        const result = await callAppsScript('generate', {
            timestamp: new Date().toISOString(),
            device: navigator.userAgent.substring(0, 100),
            ip: await getClientIP(),
            source: 'myx_shop'
        });
        
        if (result.success) {
            // 保存到本地緩存
            localStorage.setItem('myx_access_code', result.password);
            localStorage.setItem('myx_expiry', result.expiry_date);
            localStorage.setItem('myx_member', 'true');
            
            // 顯示成功信息
            showPasswordSuccess(result.password, result.expiry_date);
        } else {
            throw new Error(result.error || '生成失敗');
        }
    } catch (error) {
        console.error('雲端激活失敗:', error);
        // 降級到本地模式
        if (typeof activateLocalMembership === 'function') {
            activateLocalMembership();
        } else {
            showCustomAlert('系統錯誤，請刷新頁面重試', '錯誤');
        }
    }
}

// 2. 雲端驗證密碼
async function validateCloudPassword(password) {
    try {
        const result = await callAppsScript('validate', { password: password });
        return result;
    } catch (error) {
        console.error('雲端驗證失敗:', error);
        return { valid: false, error: '網絡錯誤' };
    }
}

// 3. 通用的 Apps Script 調用函數
async function callAppsScript(action, data = {}) {
    if (!GOOGLE_CONFIG.scriptUrl.includes('google.com')) {
        throw new Error('請配置正確的 Apps Script URL');
    }
    
    const url = `${GOOGLE_CONFIG.scriptUrl}?action=${action}`;
    
    try {
        // 如果是驗證密碼（簡單 GET）
        if (action === 'validate') {
            const params = new URLSearchParams(data).toString();
            const response = await fetch(`${url}&${params}`);
            return await response.json();
        } 
        // 其他操作使用 POST
        else {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            return await response.json();
        }
    } catch (error) {
        console.error(`調用 Apps Script 失敗 (${action}):`, error);
        throw error;
    }
}

// 4. 顯示密碼成功
function showPasswordSuccess(password, expiryDate) {
    if (typeof showCustomAlert === 'undefined') return;
    
    const expiry = new Date(expiryDate);
    const daysLeft = Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24));
    
    showCustomAlert(`
        <div style="text-align: center; padding: 20px;">
            <div style="color: #4CAF50; font-size: 3rem;">✅</div>
            <h3 style="color: #4CAF50;">付款成功！會員已激活</h3>
            
            <div style="background: #E8F5E9; border: 2px solid #4CAF50; 
                        border-radius: 10px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0 0 10px 0; font-size: 0.9rem; color: #666;">您的雲端密碼：</p>
                <div style="font-size: 1.8rem; font-weight: bold; color: #2E7D32; 
                            letter-spacing: 2px; margin: 10px 0; font-family: monospace;">
                    ${password}
                </div>
                <div style="margin-top: 15px;">
                    <div>☁️ 已保存到 Google Sheet</div>
                    <div>📅 有效期: ${expiry.toLocaleDateString('zh-CN')}</div>
                    <div>⏳ 剩餘: ${daysLeft} 天</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                <button onclick="copyToClipboard('${password}')" 
                        style="padding: 10px 20px; background: #2196F3; color: white; 
                               border: none; border-radius: 20px; cursor: pointer; font-size: 14px;">
                    📋 複製密碼
                </button>
                <button onclick="closeAlert(); setTimeout(() => location.reload(), 300);" 
                        style="padding: 10px 20px; background: #4CAF50; color: white; 
                               border: none; border-radius: 20px; cursor: pointer; font-size: 14px;">
                    🚀 進入系統
                </button>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #F5F5F5; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.85rem; color: #666;">
                    💡 <strong>重要提示：</strong>
                </p>
                <ul style="text-align: left; margin: 10px 0 0 0; padding-left: 20px; font-size: 0.85rem;">
                    <li>此密碼已保存到 Google Sheet</li>
                    <li>可在不同設備使用同一密碼</li>
                    <li>忘記密碼可聯繫客服找回</li>
                </ul>
            </div>
        </div>
    `, '激活成功');
}

// 5. 輔助函數
async function getClientIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        return '未知';
    }
}

// 6. 檢查網絡狀態
function isOnline() {
    return navigator.onLine;
}

// 7. 顯示 Google Sheet 管理鏈接
function showGoogleSheetLink() {
    if (GOOGLE_CONFIG.sheetId) {
        const sheetUrl = `https://docs.google.com/spreadsheets/d/${GOOGLE_CONFIG.sheetId}/edit`;
        window.open(sheetUrl, '_blank');
    } else {
        showCustomAlert('請先配置 Google Sheet ID', '提示');
    }
}

// 8. 雲端密碼輸入界面
function showCloudPasswordInput() {
    if (typeof showCustomAlert === 'undefined') return;
    
    showCustomAlert(`
        <div style="padding: 20px; max-width: 400px;">
            <h3 style="color: #2196F3; margin-bottom: 15px;">☁️ 雲端密碼驗證</h3>
            
            <input type="text" id="cloudPasswordInput" 
                   placeholder="輸入8位訪問密碼"
                   style="width: 100%; padding: 12px; margin-bottom: 15px; 
                          text-align: center; font-size: 1.2rem; letter-spacing: 2px;
                          border: 2px solid #ddd; border-radius: 8px;"
                   maxlength="8">
            
            <div style="display: flex; gap: 10px;">
                <button onclick="validateCloudPasswordInput()" 
                        style="flex: 1; padding: 12px; background: #4CAF50; 
                               color: white; border: none; border-radius: 8px; cursor: pointer;">
                    ✅ 驗證密碼
                </button>
                <button onclick="closeAlert()" 
                        style="flex: 1; padding: 12px; background: #f5f5f5; 
                               color: #333; border: none; border-radius: 8px; cursor: pointer;">
                    ❌ 取消
                </button>
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: #F0F7FF; border-radius: 6px;">
                <p style="margin: 0; font-size: 0.85rem; color: #2196F3;">
                    💡 密碼已保存在 Google Sheet，可在不同設備使用
                </p>
            </div>
        </div>
    `, '密碼驗證');
}

// 9. 處理密碼驗證輸入
async function validateCloudPasswordInput() {
    const passwordInput = document.getElementById('cloudPasswordInput');
    if (!passwordInput) return;
    
    const password = passwordInput.value.trim();
    
    if (password.length !== 8) {
        showCustomAlert('請輸入正確的8位密碼！', '錯誤');
        return;
    }
    
    showCustomAlert('<div class="loading">⏳ 正在驗證密碼...</div>', '請稍候');
    
    try {
        const result = await validateCloudPassword(password);
        
        if (result.valid) {
            // 保存到本地
            localStorage.setItem('myx_access_code', password);
            localStorage.setItem('myx_expiry', result.expiry_date);
            localStorage.setItem('myx_member', 'true');
            
            showCustomAlert(`
                <div style="text-align: center; padding: 20px;">
                    <div style="color: #4CAF50; font-size: 3rem;">✅</div>
                    <h3>密碼驗證成功！</h3>
                    <p>有效期至：${new Date(result.expiry_date).toLocaleDateString('zh-CN')}</p>
                    <p>剩餘 ${result.days_left} 天</p>
                    <button onclick="closeAlert(); setTimeout(() => location.reload(), 300);" 
                            style="margin-top: 15px; padding: 12px 25px; 
                                   background: #2196F3; color: white; 
                                   border: none; border-radius: 8px; cursor: pointer;">
                        進入系統
                    </button>
                </div>
            `, '驗證成功');
        } else {
            showCustomAlert(`密碼無效：${result.reason || '請檢查密碼是否正確'}`, '驗證失敗');
        }
    } catch (error) {
        showCustomAlert('網絡錯誤，請檢查連接後重試', '錯誤');
    }
}

// 10. 檢查雲端會員狀態
async function checkCloudMembershipStatus() {
    const localPassword = localStorage.getItem('myx_access_code');
    
    if (localPassword && isOnline()) {
        try {
            const result = await validateCloudPassword(localPassword);
            if (result.valid) {
                return {
                    valid: true,
                    password: localPassword,
                    expiry: result.expiry_date,
                    days_left: result.days_left,
                    source: 'cloud'
                };
            }
        } catch (error) {
            console.warn('雲端檢查失敗，使用本地緩存:', error);
        }
    }
    
    // 檢查本地緩存
    const isMember = localStorage.getItem('myx_member') === 'true';
    const expiryDateStr = localStorage.getItem('myx_expiry');
    
    if (isMember && expiryDateStr) {
        const expiryDate = new Date(expiryDateStr);
        const today = new Date();
        const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft > 0) {
            return {
                valid: true,
                password: localPassword,
                expiry: expiryDateStr,
                days_left: daysLeft,
                source: 'local'
            };
        }
    }
    
    return { valid: false };
}