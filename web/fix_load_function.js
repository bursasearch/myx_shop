// 修复loadPicksLatest函数
function loadPicksLatest() {
    console.log('🔄 开始加载 picks_latest.json...');
    
    return fetch('picks_latest.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(rawData => {
            console.log('📦 原始数据加载成功，开始适配...');
            
            // 使用适配器转换数据
            const adaptedData = window.dataAdapter.adaptPicksData(rawData);
            
            console.log(`✅ 数据适配完成: ${adaptedData.total_picks} 条记录`);
            console.log('第一条记录:', adaptedData.picks[0]);
            
            // 更新全局变量
            window.currentStockData = adaptedData;
            window.aiStocksData = adaptedData.picks;
            
            // 更新UI
            if (typeof updateStockDisplay === 'function') {
                updateStockDisplay(adaptedData.picks);
            }
            
            // 显示成功消息
            showNotification(`成功加载 ${adaptedData.total_picks} 只股票`, 'success');
            
            return adaptedData;
        })
        .catch(error => {
            console.error('❌ 加载失败:', error);
            showNotification(`加载失败: ${error.message}`, 'error');
            
            // 尝试回退方案
            return tryFallbackDataSources();
        });
}

// 回退数据源
function tryFallbackDataSources() {
    console.log('🔄 尝试回退数据源...');
    
    // 尝试加载历史数据
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0].replace(/-/g, '');
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split('T')[0].replace(/-/g, '');
    
    const fallbackFiles = [
        `history/picks_${yesterdayStr}.json`,
        `history/picks_${dateStr}.json`,
        'history/picks_latest.json'
    ];
    
    // 尝试每个文件
    for (const file of fallbackFiles) {
        console.log(`尝试: ${file}`);
        fetch(file)
            .then(r => r.json())
            .then(data => {
                console.log(`✅ 从 ${file} 加载成功`);
                const adapted = window.dataAdapter.adaptPicksData(data);
                window.aiStocksData = adapted.picks;
                showNotification(`从备份文件加载 ${adapted.total_picks} 只股票`, 'warning');
                return adapted;
            })
            .catch(e => console.log(`❌ ${file} 失败:`, e));
    }
    
    // 如果都失败，使用模拟数据
    console.log('⚠️ 所有数据源都失败，使用模拟数据');
    return createMockData();
}

// 创建模拟数据
function createMockData() {
    const mockData = {
        date: new Date().toISOString().split('T')[0],
        last_updated: new Date().toLocaleString(),
        source: '模拟数据',
        total_picks: 5,
        picks: [
            { code: '5099', name: 'CAPITALA', current_price: 0.39, daily_change: -1.27, recommendation: '🤔考慮買入' },
            { code: '4065', name: 'PPB', current_price: 11.0, daily_change: 3.58, recommendation: '🤔考慮買入' },
            { code: '5681', name: 'PETDAG', current_price: 19.76, daily_change: 1.23, recommendation: '🤔考慮買入' },
            { code: '2445', name: 'KLK', current_price: 20.0, daily_change: -0.1, recommendation: '🤔考慮買入' },
            { code: '3719', name: 'PANAMY', current_price: 7.1, daily_change: 0.71, recommendation: '🤔考慮買入' }
        ]
    };
    
    window.aiStocksData = mockData.picks;
    showNotification('使用模拟数据（请检查文件路径）', 'error');
    return mockData;
}
