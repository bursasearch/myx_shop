// 简单的股票数据
const stockData = {
    lastUpdate: new Date().toLocaleString(),
    stocks: [
        { code: "TECH", name: "科技示例", change: "+15.2%", risk: "中" },
        { code: "BANK", name: "金融示例", change: "+8.7%", risk: "低" },
        { code: "ENERGY", name: "新能源示例", change: "+22.1%", risk: "高" }
    ]
};

function getStockData() {
    return stockData;
}

console.log("股票数据脚本加载完成");
