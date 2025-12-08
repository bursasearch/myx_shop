#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const CONFIG = {
  aiOutputDir: '/data/data/com.termux/files/home/gdrive/stock_data/Myx_Data/EOD',
  websiteDataDir: './website_data',
  historyDir: './website_data/history',
  daysToKeep: 30  // 保留30天歷史數據
};

// 確保目錄存在
function ensureDirectories() {
  [CONFIG.websiteDataDir, CONFIG.historyDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`📁 創建目錄: ${dir}`);
    }
  });
}

// 尋找最新的AI選股文件
function findLatestStockFile() {
  try {
    const files = fs.readdirSync(CONFIG.aiOutputDir);
    const stockFiles = files
      .filter(f => f.startsWith('ai_selected_stocks_') && f.endsWith('.txt'))
      .sort()
      .reverse();
    
    return stockFiles.length > 0 ? stockFiles[0] : null;
  } catch (error) {
    console.error('❌ 讀取AI輸出目錄失敗:', error);
    return null;
  }
}

// 解析AI選股文件
function parseStockFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const stocks = [];
    let parsingStarted = false;
    
    for (const line of lines) {
      // 跳過標題行，直到找到股票數據
      if (line.includes('代碼') && line.includes('名稱')) {
        parsingStarted = true;
        continue;
      }
      
      if (line.includes('策略分佈:') || line.includes('市場洞察:')) {
        parsingStarted = false;
        continue;
      }
      
      if (parsingStarted && line.trim()) {
        const stock = parseStockLine(line);
        if (stock) stocks.push(stock);
      }
    }
    
    return stocks;
  } catch (error) {
    console.error('❌ 解析股票文件失敗:', error);
    return [];
  }
}

// 解析單行股票數據
function parseStockLine(line) {
  // 移除多餘空格和分隔符
  const cleanLine = line.replace(/[═─━┅]/g, '').trim();
  if (!cleanLine) return null;
  
  // 使用正則表達式匹配股票數據
  const pattern = /(\d{4}[A-Z]*)\s+([A-Z\-]+)\s+RM([\d\.]+)\s+[📈📉]([+\-\d\.]+)%\s+([\d,]+)\s+([\d\.]+)\s+([💪🔥📈].+)/;
  const match = cleanLine.match(pattern);
  
  if (match) {
    const [, code, name, price, changePercent, volume, rsi, strategyRaw] = match;
    
    // 清理策略名稱
    const strategy = strategyRaw
      .replace(/💪/, '強勢股')
      .replace(/🔥/, '超跌反彈')
      .replace(/📈/, '量價齊升')
      .replace(/[💪🔥📈]/g, '')
      .trim();
    
    // 計算AI評分 (基於RSI和策略)
    const score = calculateAIScore(parseFloat(rsi), strategy);
    
    return {
      code: code.trim(),
      name: name.trim(),
      price: parseFloat(price).toFixed(3),
      change: parseFloat(changePercent) > 0 ? 
        `+${parseFloat(changePercent).toFixed(2)}%` : 
        `${parseFloat(changePercent).toFixed(2)}%`,
      changePercent: parseFloat(changePercent),
      volume: parseInt(volume.replace(/,/g, '')),
      rsi: parseFloat(rsi),
      strategy: strategy,
      aiScore: score,
      timestamp: new Date().toISOString()
    };
  }
  
  // 嘗試另一種格式 (你的輸出格式可能不同)
  return parseAlternativeFormat(cleanLine);
}

function parseAlternativeFormat(line) {
  const parts = line.split(/\s+/).filter(p => p);
  if (parts.length >= 4) {
    const code = parts[0];
    const name = parts[1];
    const priceMatch = parts[2].match(/RM([\d\.]+)/);
    const changeMatch = parts[3].match(/[📈📉]([+\-\d\.]+)%/);
    const strategyMatch = line.match(/[💪🔥📈]([^\s💪🔥📈]+)/);
    
    if (priceMatch && changeMatch) {
      const strategy = strategyMatch ? 
        strategyMatch[1].trim() : '未分類';
      
      return {
        code: code,
        name: name,
        price: priceMatch[1],
        change: changeMatch[1].startsWith('+') ? 
          `+${changeMatch[1]}%` : 
          `${changeMatch[1]}%`,
        changePercent: parseFloat(changeMatch[1]),
        strategy: strategy,
        aiScore: 75, // 預設分數
        timestamp: new Date().toISOString()
      };
    }
  }
  
  return null;
}

// 計算AI評分
function calculateAIScore(rsi, strategy) {
  let score = 50; // 基礎分
  
  // RSI調整
  if (rsi > 70) score -= 10; // 超買
  else if (rsi < 30) score += 15; // 超賣反彈機會
  else if (rsi > 40 && rsi < 60) score += 5; // 中性偏強
  
  // 策略調整
  if (strategy.includes('強勢股')) score += 20;
  if (strategy.includes('超跌反彈')) score += 15;
  if (strategy.includes('量價齊升')) score += 10;
  
  // 確保在0-100範圍內
  return Math.min(Math.max(score, 0), 100);
}

// 生成週報數據
function generateWeeklyPerformance(stocks) {
  const today = new Date();
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - 7);
  
  // 這裡應該從歷史數據計算實際表現
  // 暫時使用模擬數據
  return {
    weekStart: weekStart.toISOString().split('T')[0],
    weekEnd: today.toISOString().split('T')[0],
    totalStocks: 35,
    avgReturn: '+8.2%',
    successRate: '72%',
    bestPerformer: {
      code: '3182',
      name: 'GENTING',
      return: '+4.5%'
    },
    worstPerformer: {
      code: '1295',
      name: 'PUBLICBANK',
      return: '-2.82%'
    },
    strategyBreakdown: {
      '強勢股': { count: 15, avgReturn: '+2.1%' },
      '超跌反彈': { count: 12, avgReturn: '+1.8%' },
      '量價齊升': { count: 8, avgReturn: '+1.5%' }
    },
    lastUpdated: today.toISOString()
  };
}

// 保存數據
function saveData(stocks, weeklyData, filename) {
  const today = new Date();
  const dateStr = today.toISOString().split('T')[0].replace(/-/g, '');
  
  // 今日數據
  const todayData = {
    updateTime: today.toISOString(),
    date: dateStr,
    totalStocks: stocks.length,
    stocks: stocks
  };
  
  // 保存今日數據
  fs.writeFileSync(
    path.join(CONFIG.websiteDataDir, 'ai_stocks_latest.json'),
    JSON.stringify(todayData, null, 2)
  );
  
  // 保存歷史備份
  fs.writeFileSync(
    path.join(CONFIG.historyDir, `ai_stocks_${dateStr}.json`),
    JSON.stringify(todayData, null, 2)
  );
  
  // 保存週報數據
  fs.writeFileSync(
    path.join(CONFIG.websiteDataDir, 'weekly_performance.json'),
    JSON.stringify(weeklyData, null, 2)
  );
  
  console.log(`✅ 保存數據完成:`);
  console.log(`   📊 今日選股: ${stocks.length} 支`);
  console.log(`   📅 歷史備份: ai_stocks_${dateStr}.json`);
  console.log(`   📈 週報數據: 已更新`);
}

// 清理舊歷史數據
function cleanupOldData() {
  try {
    const files = fs.readdirSync(CONFIG.historyDir);
    const jsonFiles = files.filter(f => f.endsWith('.json')).sort();
    
    if (jsonFiles.length > CONFIG.daysToKeep) {
      const filesToDelete = jsonFiles.slice(0, jsonFiles.length - CONFIG.daysToKeep);
      filesToDelete.forEach(file => {
        fs.unlinkSync(path.join(CONFIG.historyDir, file));
        console.log(`🗑️  刪除舊文件: ${file}`);
      });
    }
  } catch (error) {
    console.error('❌ 清理舊數據失敗:', error);
  }
}

// 提交到GitHub
function commitToGitHub() {
  try {
    console.log('🌐 提交更新到GitHub...');
    
    execSync('git add website_data/', { stdio: 'inherit' });
    execSync(`git commit -m "更新AI選股數據 ${new Date().toLocaleDateString('zh-CN')}"`, { stdio: 'inherit' });
    execSync('git push origin main', { stdio: 'inherit' });
    
    console.log('✅ GitHub更新完成！');
  } catch (error) {
    console.error('❌ GitHub提交失敗:', error.message);
  }
}

// 主函數
async function main() {
  console.log('🚀 開始更新AI選股網站數據...');
  console.log('=' .repeat(50));
  
  // 確保目錄存在
  ensureDirectories();
  
  // 尋找最新文件
  const latestFile = findLatestStockFile();
  if (!latestFile) {
    console.error('❌ 找不到AI選股輸出文件');
    process.exit(1);
  }
  
  const filePath = path.join(CONFIG.aiOutputDir, latestFile);
  console.log(`📂 找到最新文件: ${latestFile}`);
  
  // 解析數據
  const stocks = parseStockFile(filePath);
  if (stocks.length === 0) {
    console.error('❌ 未解析到有效股票數據');
    process.exit(1);
  }
  
  console.log(`📊 解析到 ${stocks.length} 支股票:`);
  stocks.forEach((stock, i) => {
    console.log(`  ${i+1}. ${stock.code} ${stock.name} ${stock.price} ${stock.change} [${stock.strategy}]`);
  });
  
  // 生成週報數據
  const weeklyData = generateWeeklyPerformance(stocks);
  
  // 保存數據
  saveData(stocks, weeklyData, latestFile);
  
  // 清理舊數據
  cleanupOldData();
  
  // 提交到GitHub（可選）
  const shouldPush = process.argv.includes('--push');
  if (shouldPush) {
    commitToGitHub();
  }
  
  console.log('=' .repeat(50));
  console.log('🎉 AI選股網站數據更新完成！');
  console.log(`🔗 數據文件: ${CONFIG.websiteDataDir}/`);
  
  // 返回成功
  return stocks.length;
}

// 執行
main().catch(console.error);
