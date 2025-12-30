#!/usr/bin/env python3
"""
简化版AI选股器 - 专门为您的规范化EOD数据设计
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

def load_normalized_data(csv_path):
    """加载规范化CSV数据"""
    print(f"📊 加载数据: {os.path.basename(csv_path)}")
    
    df = pd.read_csv(csv_path)
    
    # 数据清理
    df['Code'] = df['Code'].astype(str).str.strip()
    df['Stock'] = df['Stock'].astype(str).str.strip()
    df['Sector'] = df['Sector'].astype(str).str.strip()
    
    # 转换Chg列为数值
    def parse_change(chg_str):
        if isinstance(chg_str, str):
            chg_clean = chg_str.replace('%', '').replace('+', '').strip()
            if chg_clean == '-':
                return 0.0
            try:
                return float(chg_clean)
            except:
                return 0.0
        elif pd.isna(chg_str):
            return 0.0
        else:
            return float(chg_str)
    
    df['Chg_Numeric'] = df['Chg'].apply(parse_change)
    
    # 转换其他数值列
    numeric_cols = ['Last', 'Open', 'High', 'Low', 'Prv Close', 'Vol', 
                   'Vol MA (20)', 'RSI (14)', 'P/E']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"  加载 {len(df)} 行数据")
    return df

def calculate_stock_scores(df):
    """计算股票评分"""
    print("🧮 计算股票评分...")
    
    scores = []
    
    for idx, row in df.iterrows():
        score = 50  # 基础分
        
        try:
            # 1. 涨跌幅评分 (权重: 40%)
            chg = row.get('Chg_Numeric', 0)
            if chg > 5:
                score += 20
            elif chg > 2:
                score += 10
            elif chg > 0:
                score += 5
            elif chg < -5:
                score -= 10
            elif chg < 0:
                score -= 5
            
            # 2. 成交量评分 (权重: 25%)
            volume = row.get('Vol', 0)
            if volume > 1000000:
                score += 15
            elif volume > 100000:
                score += 10
            elif volume > 10000:
                score += 5
            elif volume < 1000:
                score -= 5
            
            # 3. RSI评分 (权重: 20%)
            rsi = row.get('RSI (14)', 50)
            if 30 < rsi < 70:
                score += 10
            elif rsi < 30:
                score += 15  # 超卖，可能反弹
            elif rsi > 70:
                score -= 5   # 超买
            
            # 4. 市值/价格稳定性 (权重: 15%)
            last_price = row.get('Last', 0)
            if last_price > 1.0:
                score += 5
            elif last_price > 0.5:
                score += 3
            
            # 5. 排除状态不是Active的
            status = row.get('Status', '')
            if status != 'Active':
                score -= 20
            
            # 确保分数在0-100之间
            score = max(0, min(100, score))
            
        except Exception as e:
            print(f"  警告: 计算{row.get('Code', '未知')}评分时出错: {e}")
            score = 50
        
        scores.append(score)
    
    df = df.copy()
    df['Score'] = scores
    return df

def generate_recommendations(df_sorted):
    """生成选股推荐"""
    print("🎯 生成推荐...")
    
    recommendations = []
    
    for rank, (idx, row) in enumerate(df_sorted.iterrows(), 1):
        score = row['Score']
        chg = row['Chg_Numeric']
        volume = row.get('Vol', 0)
        
        # 确定推荐级别
        if score >= 80:
            rec_level = "强力买入"
            risk = "低"
            color = "green"
        elif score >= 70:
            rec_level = "买入"
            risk = "中低"
            color = "lightgreen"
        elif score >= 60:
            rec_level = "考虑买入"
            risk = "中等"
            color = "yellow"
        elif score >= 50:
            rec_level = "中性"
            risk = "中高"
            color = "orange"
        else:
            rec_level = "观望"
            risk = "高"
            color = "red"
        
        # 生成理由
        reasons = []
        if chg > 2:
            reasons.append("涨势良好")
        if volume > 100000:
            reasons.append("成交活跃")
        if row.get('RSI (14)', 50) < 40:
            reasons.append("RSI显示超卖")
        if row.get('RSI (14)', 50) > 60:
            reasons.append("RSI显示强势")
        
        if not reasons:
            reasons.append("综合评分推荐")
        
        recommendation = {
            'rank': rank,
            'code': str(row['Code']),
            'name': str(row['Stock']),
            'sector': str(row['Sector']),
            'current_price': float(row.get('Last', 0)),
            'daily_change': float(chg),
            'volume': int(volume),
            'score': float(score),
            'recommendation': rec_level,
            'risk_level': risk,
            'color': color,
            'reasons': ", ".join(reasons[:3]),
            'rsi': float(row.get('RSI (14)', 0)),
            'pe_ratio': float(row.get('P/E', 0)),
            'dividend_yield': str(row.get('DY*', '-')),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        recommendations.append(recommendation)
    
    return recommendations

def save_json(data, filepath):
    """保存JSON文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 保存: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 保存失败 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("🤖 AI选股器 - 简化版")
    print("="*60)
    
    # 配置路径
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
    WEB_DIR = os.path.join(BASE_DIR, "web")
    
    # 确保目录存在
    os.makedirs(WEB_DIR, exist_ok=True)
    
    # 获取最新的规范化CSV
    normalized_dir = "./normalized_now"
    if not os.path.exists(normalized_dir):
        print(f"❌ 目录不存在: {normalized_dir}")
        return
    
    csv_files = [f for f in os.listdir(normalized_dir) if f.endswith('.csv')]
    if not csv_files:
        print("❌ 没有CSV文件")
        return
    
    csv_files.sort(reverse=True)
    input_csv = os.path.join(normalized_dir, csv_files[0])
    
    print(f"📁 输入文件: {os.path.basename(input_csv)}")
    print(f"📂 输出目录: {WEB_DIR}")
    
    # 处理流程
    print("\n" + "="*60)
    
    # 1. 加载数据
    df = load_normalized_data(input_csv)
    
    # 2. 计算评分
    df_scored = calculate_stock_scores(df)
    
    # 3. 排序并选择前20
    df_sorted = df_scored.sort_values('Score', ascending=False).head(20)
    
    # 4. 生成推荐
    recommendations = generate_recommendations(df_sorted)
    
    # 5. 保存结果
    output_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_picks': len(recommendations),
        'market': 'Bursa Malaysia',
        'source_file': os.path.basename(input_csv),
        'picks': recommendations
    }
    
    # 保存文件
    output_path = os.path.join(WEB_DIR, 'ai_picks.json')
    if save_json(output_data, output_path):
        print(f"\n✅ AI选股完成!")
        print(f"   推荐 {len(recommendations)} 支股票")
        
        # 显示前5个推荐
        print("\n🏆 前5推荐:")
        for pick in recommendations[:5]:
            print(f"  {pick['rank']:2}. {pick['code']:8} {pick['name']:15} "
                  f"评分: {pick['score']:5.1f} - {pick['recommendation']}")
    
    print("\n" + "="*60)
    print("🌐 文件已生成，可以用于 retail-inv.html")
    print("="*60)

if __name__ == "__main__":
    main()
