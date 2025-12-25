#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const DATA_DIR = './website_data';
const HISTORY_DIR = './website_data/history';

// 生成簡單的週報
function generateWeeklyReport() {
  console.log('📊 生成AI選股週報...');
  
  // 收集本週數據
  const weekFiles = [];
  const today = new Date();
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dateStr = date.toISOString().split('T')[0].replace(/-/g, '');
    const filePath = path.join(HISTORY_DIR, `ai_stocks_${dateStr}.json`);
    
    if (fs.existsSync(filePath)) {
      weekFiles.push({ date: dateStr, file: filePath });
    }
  }
  
  if (weekFiles.length === 0) {
    console.log('⚠️  沒有本週數據');
    return;
  }
  
  // 分析本週表現
  const analysis = {
    weekStart: weekFiles[weekFiles.length - 1].date,
    weekEnd: weekFiles[0].date,
    totalDays: weekFiles.length,
    totalStocks: 0,
    strategyBreakdown: {},
    bestPerformers: []
  };
  
  weekFiles.forEach(({ date, file }) => {
    try {
      const data = JSON.parse(fs.readFileSync(file, 'utf8'));
      analysis.totalStocks += data.stocks.length;
      
      // 分析策略分佈
      data.stocks.forEach(stock => {
        if (!analysis.strategyBreakdown[stock.strategy]) {
          analysis.strategyBreakdown[stock.strategy] = 0;
        }
        analysis.strategyBreakdown[stock.strategy]++;
      });
      
      // 找出當日最佳
      if (data.stocks.length > 0) {
        const best = data.stocks.reduce((prev, current) => 
          prev.changePercent > current.changePercent ? prev : current
        );
        analysis.bestPerformers.push({
          date: date,
          code: best.code,
          name: best.name,
          return: best.change
        });
      }
    } catch (error) {
      console.warn(`無法讀取文件 ${file}:`, error.message);
    }
  });
  
  // 生成HTML週報
  const html = generateHTMLReport(analysis);
  
  // 保存
  fs.writeFileSync(
    path.join(DATA_DIR, 'weekly_report.html'),
    html
  );
  
  // 更新週報數據
  fs.writeFileSync(
    path.join(DATA_DIR, 'weekly_performance.json'),
    JSON.stringify(analysis, null, 2)
  );
  
  console.log(`✅ 週報生成完成：${weekFiles.length} 天數據，${analysis.totalStocks} 支股票`);
}

function generateHTMLReport(analysis) {
  return `
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI選股週報 ${analysis.weekStart} - ${analysis.weekEnd}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem; border-radius: 10px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }
    .stat-card { background: #f7fafc; padding: 1.5rem; border-radius: 8px; text-align: center; }
    table { width: 100%; border-collapse: collapse; margin: 2rem 0; }
    th, td { padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }
    th { background: #edf2f7; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🤖 AI選股週報</h1>
    <p>${analysis.weekStart} 至 ${analysis.weekEnd} | ${analysis.totalDays} 個交易日</p>
  </div>
  
  <div class="stats">
    <div class="stat-card">
      <h3>總選股數</h3>
      <p style="font-size: 2rem; font-weight: bold;">${analysis.totalStocks}</p>
    </div>
    <div class="stat-card">
      <h3>交易日</h3>
      <p style="font-size: 2rem; font-weight: bold;">${analysis.totalDays}</p>
    </div>
    <div class="stat-card">
      <h3>平均每日</h3>
      <p style="font-size: 2rem; font-weight: bold;">${Math.round(analysis.totalStocks / analysis.totalDays)}</p>
    </div>
  </div>
  
  <h2>📊 策略分佈</h2>
  <table>
    <thead>
      <tr><th>策略</th><th>數量</th><th>比例</th></tr>
    </thead>
    <tbody>
      ${Object.entries(analysis.strategyBreakdown).map(([strategy, count]) => `
        <tr>
          <td>${strategy}</td>
          <td>${count}</td>
          <td>${((count / analysis.totalStocks) * 100).toFixed(1)}%</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
  
  <h2>🏆 每日最佳表現</h2>
  <table>
    <thead>
      <tr><th>日期</th><th>股票代碼</th><th>名稱</th><th>漲幅</th></tr>
    </thead>
    <tbody>
      ${analysis.bestPerformers.map(perf => `
        <tr>
          <td>${perf.date}</td>
          <td><strong>${perf.code}</strong></td>
          <td>${perf.name}</td>
          <td style="color: ${perf.return.includes('+') ? 'green' : 'red'}">${perf.return}</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
  
  <div style="margin-top: 3rem; padding: 1rem; background: #f0f4f8; border-radius: 8px;">
    <p>📅 <strong>報告生成時間：</strong>${new Date().toLocaleString('zh-CN')}</p>
    <p>⚠️ <strong>免責聲明：</strong>本報告僅供參考，不構成投資建議。</p>
  </div>
</body>
</html>
  `;
}

// 主程序
if (require.main === module) {
  generateWeeklyReport();
}
