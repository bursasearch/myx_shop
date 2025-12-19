#!/usr/bin/env python3
"""
行业分析报告脚本
"""

import json
import pandas as pd
import os
from datetime import datetime

def generate_sector_report():
    """生成行业分析报告"""
    
    # 读取行业映射
    with open('sector_mapping.json', 'r') as f:
        sector_mapping = json.load(f)
    
    # 读取最新的规范化数据
    data_file = '../web/normalized_stocks.csv'
    
    if not os.path.exists(data_file):
        print("❌ 数据文件不存在")
        return
    
    df = pd.read_csv(data_file)
    
    print("="*60)
    print("🏢 行业分析报告")
    print(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 检查必要的列
    if 'Sector' not in df.columns:
        print("❌ 数据中没有Sector列")
        return
    
    # 行业分布
    sector_counts = df['Sector'].value_counts()
    
    print(f"\n📊 行业分布 (总计 {len(df)} 支股票):")
    print("-" * 50)
    
    for sector, count in sector_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{sector:<40} {count:>4} 支 ({percentage:>5.1f}%)")
    
    # 按行业的价格统计
    if 'Last' in df.columns:
        print(f"\n💰 各行业平均价格:")
        print("-" * 50)
        
        sector_stats = df.groupby('Sector')['Last'].agg(['mean', 'min', 'max', 'count'])
        sector_stats = sector_stats.sort_values('mean', ascending=False)
        
        for sector, stats in sector_stats.iterrows():
            print(f"{sector:<40} 平均: RM{stats['mean']:.3f}  "
                  f"范围: RM{stats['min']:.3f}-{stats['max']:.3f}  "
                  f"({int(stats['count'])} 支)")
    
    # 按行业的涨跌幅统计
    if 'Chg%' in df.columns:
        print(f"\n📈 各行业涨跌幅:")
        print("-" * 50)
        
        sector_changes = df.groupby('Sector')['Chg%'].agg(['mean', 'count'])
        sector_changes = sector_changes.sort_values('mean', ascending=False)
        
        for sector, stats in sector_changes.iterrows():
            change_color = "🟢" if stats['mean'] > 0 else "🔴" if stats['mean'] < 0 else "⚪"
            print(f"{change_color} {sector:<38} 平均: {stats['mean']:>+6.2f}%  "
                  f"({int(stats['count'])} 支)")
    
    # 生成JSON报告
    report = {
        "report_date": datetime.now().strftime('%Y-%m-%d'),
        "report_time": datetime.now().strftime('%H:%M:%S'),
        "total_stocks": len(df),
        "sectors_count": len(sector_counts),
        "sector_distribution": sector_counts.to_dict(),
        "generated_at": datetime.now().isoformat()
    }
    
    # 保存报告
    report_file = '../web/sector_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 报告已保存: {report_file}")
    print("="*60)

if __name__ == "__main__":
    generate_sector_report()
