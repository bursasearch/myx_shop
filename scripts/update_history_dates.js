// 自动更新历史日期选择器
console.log('🔄 更新历史日期选择器...');

// 获取history目录中的文件
fetch('history/')
  .then(response => response.text())
  .then(html => {
    // 解析HTML获取文件列表
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const links = Array.from(doc.querySelectorAll('a[href$=".json"]'));
    
    // 提取日期
    const dates = links
      .map(link => link.getAttribute('href'))
      .filter(href => href.startsWith('picks_'))
      .map(href => href.replace('picks_', '').replace('.json', ''))
      .sort()
      .reverse();  // 最新的在前面
    
    console.log('找到历史文件日期:', dates);
    
    // 更新日期选择器
    const dateSelect = document.getElementById('dateSelect');
    if (dateSelect) {
      // 保存当前选中的值
      const currentValue = dateSelect.value;
      
      // 清空现有选项（保留第一个选项）
      while (dateSelect.options.length > 1) {
        dateSelect.remove(1);
      }
      
      // 添加历史日期选项
      dates.forEach(dateStr => {
        // 将YYYYMMDD转换为YYYY-MM-DD
        const year = dateStr.substring(0, 4);
        const month = dateStr.substring(4, 6);
        const day = dateStr.substring(6, 8);
        const formattedDate = `${year}-${month}-${day}`;
        
        const option = document.createElement('option');
        option.value = formattedDate;
        option.textContent = formattedDate;
        dateSelect.appendChild(option);
      });
      
      // 恢复之前选中的值，或者选择最新的
      const hasCurrent = Array.from(dateSelect.options).some(opt => opt.value === currentValue);
      if (!hasCurrent && dates.length > 0) {
        const latestDate = dates[0];
        const year = latestDate.substring(0, 4);
        const month = latestDate.substring(4, 6);
        const day = latestDate.substring(6, 8);
        dateSelect.value = `${year}-${month}-${day}`;
      }
      
      console.log('日期选择器已更新');
    }
  })
  .catch(error => {
    console.log('无法获取历史文件列表，使用默认日期:', error);
    // 使用默认的最近7天
    initDefaultDates();
  });

// 初始化默认日期
function initDefaultDates() {
  const dateSelect = document.getElementById('dateSelect');
  if (!dateSelect) return;
  
  // 生成最近7天的日期
  for (let i = 0; i < 7; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    // 检查是否已存在该选项
    const exists = Array.from(dateSelect.options).some(opt => opt.value === dateStr);
    if (!exists) {
      const option = document.createElement('option');
      option.value = dateStr;
      option.textContent = dateStr + (i === 0 ? ' (今天)' : '');
      if (i === 0) option.selected = true;
      dateSelect.appendChild(option);
    }
  }
}

// 如果没有找到history目录，使用默认日期
setTimeout(initDefaultDates, 1000);
