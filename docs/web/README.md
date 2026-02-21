# AI选股数据目录

## 文件说明
- `picks_latest.json` - 最新AI选股推荐
- `latest_price.json` - 最新股价数据
- `data.json` - 简化版数据
- `picks_history.js` - 历史数据JavaScript格式
- `date_config.js` - 日期配置

## 历史数据
历史数据存储在 `history/` 目录中，格式为 `picks_YYYYMMDD.json`

## 更新信息
- 最后同步: Thu Feb 12 09:54:40 +08 2026
- 数据版本: 20260212-095440
- 数据源: EOD CSV文件

## 使用方式
这些数据被以下页面使用:
1. `ai-monitor.html` - AI监控仪表板
2. `bursa.html` - Bursa Malaysia分析工具

## 自动化流程
数据通过 `sync_ai_data.sh` 脚本自动同步
每天收盘后自动运行
