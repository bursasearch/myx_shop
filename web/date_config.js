// date_config.js - 自动生成于 $(date '+%Y-%m-%d %H:%M:%S')
// 兼容性版本 - 保持原有函数，添加增强功能

// ================ 日期配置数据 ================
window.availableDates = [];

// ================ 1. 原始函数（完全保留） ================

// 检测是否在GitHub Pages上运行
window.isGitHubPages = window.location.hostname.includes('github.io');

// 获取正确的文件路径
window.getDataFilePath = function(dateId) {
    const date = window.availableDates.find(d => d.id === dateId);
    if (!date) return null;
    
    if (window.isGitHubPages) {
        // GitHub Pages使用相对路径
        return './' + date.file;
    } else {
        // 本地使用相对路径
        return date.file;
    }
};

// 获取日期显示名称
window.getDateDisplay = function(dateId) {
    const date = window.availableDates.find(d => d.id === dateId);
    return date ? date.display : dateId;
};

// 检查日期是否存在
window.isDateAvailable = function(dateId) {
    return window.availableDates.some(d => d.id === dateId);
};

// 加载历史数据（兼容新旧版本）
window.loadHistoryData = function(dateId) {
    // 先尝试从allHistoryData加载
    if (window.allHistoryData && window.allHistoryData[dateId]) {
        return Promise.resolve(window.allHistoryData[dateId].data);
    }
    
    // 从文件加载
    const filePath = window.getDataFilePath(dateId);
    if (!filePath) {
        return Promise.reject(new Error('文件路径不存在'));
    }
    
    return fetch(filePath)
        .then(response => {
            if (!response.ok) throw new Error('加载失败: ' + response.status);
            return response.json();
        })
        .catch(error => {
            console.error('加载历史数据失败:', error);
            throw error;
        });
};

// ================ 2. 智能初始化日期数据 ================
(function initializeDates() {
    console.log('📅 初始化日期数据...');
    
    // 如果有 all_history.js，从中获取日期
    if (window.allHistoryData && Object.keys(window.allHistoryData).length > 0) {
        console.log('✅ 从 all_history.js 获取日期');
        const dates = Object.keys(window.allHistoryData).sort();
        buildAvailableDates(dates);
        return;
    }
    
    // 否则使用脚本生成的日期数据
    console.log('✅ 使用脚本生成的日期数据');
    // availableDates 会在下面由脚本填充
})();

function buildAvailableDates(dateIds) {
    window.availableDates = dateIds.map(dateId => {
        const year = dateId.substring(0, 4);
        const month = dateId.substring(4, 6);
        const day = dateId.substring(6, 8);
        return {
            id: dateId,
            display: \`\${year}-\${month}-\${day}\`,
            file: \`history/picks_\${dateId}.json\`
        };
    }).sort((a, b) => b.id.localeCompare(a.id));
    
    // 设置默认日期
    if (window.availableDates.length > 0) {
        window.defaultDate = window.availableDates[0].id;
        window.latestDate = window.availableDates[0];
        console.log(\`📅 找到 \${window.availableDates.length} 个日期，默认: \${window.latestDate.display}\`);
    }
}

// ================ 3. 脚本生成的数据部分 ================
// 以下数据由脚本自动生成
window.availableDates = [
  {id: '20260126', display: '2026-01-26', file: 'history/picks_20260126.json'},
  {id: '20260127', display: '2026-01-27', file: 'history/picks_20260127.json'},
  {id: '20260128', display: '2026-01-28', file: 'history/picks_20260128.json'},
  {id: '20260129', display: '2026-01-29', file: 'history/picks_20260129.json'},
  {id: '20260130', display: '2026-01-30', file: 'history/picks_20260130.json'},
];

// 默认选中最新日期
if (window.availableDates.length > 0) {
    window.defaultDate = window.availableDates[0].id;
    window.latestDate = window.availableDates[0];
}

console.log('🚀 date_config.js 加载完成');
