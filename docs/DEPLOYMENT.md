# 部署报告
- 部署时间: 2026-02-20 14:29:09
- 源目录: /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop
- 目标目录: /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop/docs

## 已部署文件
- ✅ ai-monitor.html - AI选股监控仪表板
- ✅ klse-guide.html - KLSE Screener使用指南
- ✅ web/ - AI选股数据文件
- ✅ 更新了index.html导航链接

## GitHub Pages访问地址
网站将在以下地址可用:
https://[您的GitHub用户名].github.io/[仓库名]/

## 重要文件说明
1. `ai-monitor.html` - 主监控页面
   - 实时显示AI选股
   - 提供KLSE设置指导
   - 生成导入文件

2. `klse-guide.html` - 详细使用教程
   - 盈利目标设置
   - 止损设置
   - 批量操作技巧

3. `web/`目录 - 数据文件
   - picks_latest.json - 最新AI选股
   - latest_price.json - 最新价格
   - history/ - 历史数据

## 更新频率
- 数据更新: 每个交易日收盘后
- 页面更新: 自动同步
- 完全部署: 运行此脚本

## 手动操作步骤
如果需要手动更新GitHub Pages:
```bash
cd /data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop/docs
git add .
git commit -m "更新AI选股监控系统 - 2026-02-20 14:29:09"
git push origin main
```
