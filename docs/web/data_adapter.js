// data_adapter.js - 数据格式适配器
// 用于适配不同格式的JSON数据

window.dataAdapter = {
    // 转换picks_latest.json为HTML期望的格式
    adaptPicksData: function(rawData) {
        console.log('原始数据格式:', Array.isArray(rawData) ? '数组' : typeof rawData);
        
        if (Array.isArray(rawData)) {
            // 已经是数组格式，直接返回
            console.log('✅ 数据已经是数组格式，包含', rawData.length, '条记录');
            return {
                date: new Date().toISOString().split('T')[0],
                last_updated: new Date().toLocaleString(),
                source: 'picks_latest.json',
                total_picks: rawData.length,
                picks: rawData
            };
        } else if (rawData && typeof rawData === 'object') {
            // 可能是字典格式，尝试提取
            console.log('数据是对象格式，键:', Object.keys(rawData));
            
            // 尝试不同的键名
            const possibleKeys = ['picks', 'stocks', 'data', 'items', 'recommendations'];
            for (const key of possibleKeys) {
                if (Array.isArray(rawData[key])) {
                    console.log(`✅ 找到数组数据在键 "${key}" 下，包含`, rawData[key].length, '条记录');
                    return {
                        date: rawData.date || new Date().toISOString().split('T')[0],
                        last_updated: rawData.last_updated || new Date().toLocaleString(),
                        source: rawData.source || 'picks_latest.json',
                        total_picks: rawData[key].length,
                        picks: rawData[key]
                    };
                }
            }
            
            // 如果都没找到，尝试将整个对象转换为数组
            console.log('⚠️ 未找到标准格式，尝试转换...');
            const picks = [];
            for (const [code, info] of Object.entries(rawData)) {
                if (info && typeof info === 'object') {
                    picks.push({
                        code: code,
                        name: info.name || info.stock || 'N/A',
                        current_price: info.price || info.current_price || 0,
                        daily_change: info.change || info.daily_change || 0,
                        recommendation: info.recommendation || '🤔考慮買入',
                        rank: picks.length + 1
                    });
                }
            }
            
            return {
                date: new Date().toISOString().split('T')[0],
                last_updated: new Date().toLocaleString(),
                source: 'picks_latest.json (转换后)',
                total_picks: picks.length,
                picks: picks
            };
        }
        
        console.error('❌ 无法识别的数据格式');
        return {
            date: new Date().toISOString().split('T')[0],
            last_updated: new Date().toLocaleString(),
            source: 'picks_latest.json',
            total_picks: 0,
            picks: []
        };
    }
};

console.log('📦 数据适配器已加载');
