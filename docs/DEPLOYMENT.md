# 部署报告
- 部署时间: 2026-02-24 19:05:48
- 源目录: /storage/emulated/0/bursasearch/myx_shop
- 目标目录: /storage/emulated/0/bursasearch/myx_shop/docs

## 已部署文件
- ✅ ai-monitor.html - AI选股监控仪表板
- ✅ klse-guide.html - KLSE Screener使用指南
- ✅ web/ - AI选股数据文件
- ✅ bursa.html - AI投资计算器

## GitHub Pages访问地址
- 主页: https://bursasearch.github.io/myx_shop/
- AI监控: https://bursasearch.github.io/myx_shop/ai-monitor.html
- 投资计算器: https://bursasearch.github.io/myx_shop/bursa.html

## 重要文件说明
1. `ai-monitor.html` - 主监控页面
   - 实时显示AI选股
   - 提供KLSE设置指导
   - 生成导入文件

2. `bursa.html` - AI投资计算器
   - 今日AI推荐
   - 交易成本计算
   - 历史数据查询

3. `web/`目录 - 数据文件
   - picks_latest.json - 最新AI选股
   - latest_price.json - 最新价格
   - history/ - 历史数据

## 更新频率
- 数据更新: 每个交易日收盘后
- 页面更新: 自动同步

## 手动操作步骤
如果需要手动更新GitHub Pages:
```bash
cd /storage/emulated/0/bursasearch/myx_shop/docs
git add .
git commit -m "更新AI选股监控系统 - 2026-02-24 19:05:48"
git push origin master
```
