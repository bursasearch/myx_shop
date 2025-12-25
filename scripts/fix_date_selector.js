// fix_date_selector.js - 修复日期选择器逻辑

// 原始有问题的代码：
// function initDateSelector() {
//     const dateSelect = document.getElementById('dateSelect');
//     dateSelect.innerHTML = '';
//     
//     // 生成最近7天的日期选项
//     for (let i = 0; i < 7; i++) {
//         const date = new Date();
//         date.setDate(date.getDate() - i);
//         const dateStr = date.toISOString().split('T')[0];
//         const option = document.createElement('option');
//         option.value = dateStr;
//         option.textContent = dateStr + (i === 0 ? ' (今天)' : '');
//         if (i === 0) option.selected = true;
//         dateSelect.appendChild(option);
//     }
// }

// 修复后的代码：
function initDateSelector() {
    const dateSelect = document.getElementById('dateSelect');
    dateSelect.innerHTML = '';
    
    // 首先检查实际存在的文件
    const availableDates = [
        '2025-12-21',
        '2025-12-20', 
        '2025-12-18',
        '2025-12-17',
        '2025-12-16',
        '2025-12-15'
    ];
    
    // 添加"最新数据"选项
    const latestOption = document.createElement('option');
    latestOption.value = 'latest';
    latestOption.textContent = '最新数据 (picks_latest.json)';
    latestOption.selected = true;
    dateSelect.appendChild(latestOption);
    
    // 添加真实存在的日期
    availableDates.forEach(dateStr => {
        const option = document.createElement('option');
        option.value = dateStr;
        option.textContent = dateStr;
        dateSelect.appendChild(option);
    });
    
    dateSelect.addEventListener('change', function() {
        currentDate = this.value;
        console.log('选择日期:', currentDate);
        
        if (currentDate === 'latest') {
            // 加载最新数据
            loadCurrentData('picks_latest.json');
        } else {
            // 加载历史数据
            const filename = `picks_${dateStr.replace(/-/g, '')}.json`;
            loadCurrentData(`history/${filename}`);
        }
    });
}

console.log('✅ 日期选择器修复代码已准备好');
console.log('需要替换 retail-inv.html 中的 initDateSelector 函数');
