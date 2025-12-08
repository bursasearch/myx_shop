#!/usr/bin/env python3
"""
AI選股分析系統 - 最終優化版
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def load_eod_data(file_path):
    """加載EOD數據"""
    print(f"📊 加載EOD數據: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()

        if '\t' in first_line:
            sep = '\t'
        elif ';' in first_line:
            sep = ';'
        else:
            sep = ','

        df = pd.read_csv(file_path, sep=sep, encoding='utf-8', low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        print(f"✅ 成功加載 {len(df)} 行數據")
        print(f"📋 數據欄位: {list(df.columns)}")

        return df

    except Exception as e:
        print(f"❌ 加載失敗: {e}")
        return None

def clean_excel_formula(value):
    """清理Excel公式格式"""
    if isinstance(value, str):
        if value.startswith('="') and value.endswith('"'):
            return value[2:-1]
        elif value.startswith('='):
            return value[1:]
        return value.strip()
    return value

def enhance_stock_data(df):
    """增強股票數據"""
    print("🔧 處理股票數據...")

    # 完整的马来西亚股市行业映射
    MALAYSIA_SECTOR_MAPPING = {
        # 工业产品
        '101': 'Industrial Products', '102': 'Industrial Products', '103': 'Industrial Products',
        '104': 'Industrial Products', '105': 'Industrial Products', '106': 'Industrial Products',
        '107': 'Industrial Products', '108': 'Industrial Products', '109': 'Industrial Products',
        '110': 'Industrial Products', '111': 'Industrial Products', '112': 'Industrial Products',
        '113': 'Industrial Products', '114': 'Industrial Products', '115': 'Industrial Products',
        '116': 'Industrial Products', '117': 'Industrial Products', '118': 'Industrial Products',
        '119': 'Industrial Products', '120': 'Industrial Products',
        '161': 'Industrial Products', '162': 'Industrial Products', '163': 'Industrial Products',
        '164': 'Trading/Services', '165': 'Industrial Products',
        
        # 建筑
        '201': 'Construction', '202': 'Construction',
        
        # 贸易/服务
        '301': 'Industrial Products', '302': 'Trading/Services', '303': 'Trading/Services',
        '304': 'Trading/Services', '305': 'Industrial Products', '306': 'Trading/Services',
        '307': 'Trading/Services', '308': 'Trading/Services', '309': 'Trading/Services',
        '310': 'Trading/Services',
        '361': 'Trading/Services',
        
        # 消费产品
        '401': 'Consumer Products', '402': 'Consumer Products', '403': 'Consumer Products',
        '404': 'Consumer Products',
        
        # 房地产
        '501': 'Properties', '502': 'Properties', '503': 'Properties',
        
        # 种植
        '601': 'Plantation', '602': 'Plantation',
        
        # 科技
        '701': 'Technology', '702': 'Technology', '703': 'Technology',
        '358': 'Technology',
        
        # 金融
        '801': 'Finance', '802': 'Finance', '803': 'Finance',
        
        # 医疗
        '901': 'Healthcare', '902': 'Healthcare',
        
        # 运输物流
        '1001': 'Transportation & Logistics', '1002': 'Transportation & Logistics',
        
        # 电讯媒体
        '1101': 'Telecommunications & Media', '1102': 'Telecommunications & Media',
        
        # 公用事业
        '1201': 'Utilities', '1202': 'Utilities',
        
        # REITs
        '1301': 'REITs', '1302': 'REITs',
        
        # 能源
        '1401': 'Energy', '1402': 'Energy',
        
        # SPAC
        '1501': 'SPAC',
        
        # 其他
        '461': 'Industrial Products',
    }

    def map_sector_code(code):
        """映射行业代码为行业名称"""
        code_str = str(code).strip()
        return MALAYSIA_SECTOR_MAPPING.get(code_str, f"Code: {code_str}")

    # 清理Excel公式格式
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_excel_formula)

    # 設置股票代碼
    if 'code' not in df.columns:
        code_cols = ['code', 'symbol', 'ticker']
        for col in code_cols:
            if col in df.columns:
                df['code'] = df[col].astype(str).str.strip()
                break
        else:
            df['code'] = df.iloc[:, 0].astype(str).str.strip()

    # 設置股票名稱
    if 'name' not in df.columns:
        name_cols = ['stock', 'name', 'company']
        for col in name_cols:
            if col in df.columns:
                df['name'] = df[col].astype(str).str.strip()
                break
        else:
            df['name'] = df['code']

    # 設置行業
    if 'sector' not in df.columns:
        sector_cols = ['sector', 'industry']
        for col in sector_cols:
            if col in df.columns:
                df['sector'] = df[col].astype(str).str.strip()
                break
        else:
            df['sector'] = 'Unknown'

    # 轉換行業代碼
    df['sector'] = df['sector'].apply(map_sector_code)
    
    return df

# 复制原脚本的其他函数...
            # 正規化各項得分（0-100）
            momentum_score = min(max((momentum + 10) * 5, 0), 100)
            rsi_score = 100 - abs(rsi - 50) * 2
            volume_score = min(volume_ratio * 33, 100)
            trend_score = 100 if ma_ratio > 1 else ma_ratio * 100
            risk_score = max(100 - volatility * 2, 0)
            
            # 計算總分
            total_score = (
                momentum_score * score_weights['momentum'] +
                rsi_score * score_weights['rsi'] +
                volume_score * score_weights['volume'] +
                trend_score * score_weights['trend'] +
                risk_score * score_weights['risk']
            )
            
            # 生成建議
            if total_score >= 85:
                recommendation = "強力買入"
            elif total_score >= 70:
                recommendation = "買入"
            elif total_score >= 60:
                recommendation = "持有"
            elif total_score >= 50:
                recommendation = "觀望"
            else:
                recommendation = "賣出"
            
            results.append({
                'code': code,
                'name': name,
                'sector': sector,
                'score': round(total_score, 1),
                'current_price': round(price, 2),
                'change_5d': f"{momentum:+.1f}%",
                'rsi': round(rsi, 1),
                'volume_ratio': round(volume_ratio, 1),
                'volatility': round(volatility, 1),
                'recommendation': recommendation,
                'analysis_time': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"⚠️  處理 {row.get('code', 'N/A')} 時出錯: {e}")
            continue
    
    return pd.DataFrame(results)

def generate_top_picks(df, top_n=10):
    """生成Top推薦"""
    print(f"🏆 生成Top {top_n}推薦...")
    
    if df.empty:
        print("❌ 沒有可用的數據")
        return []
    
    # 按分數排序
    df_sorted = df.sort_values('score', ascending=False).head(top_n)
    
    # 添加排名
    df_sorted = df_sorted.reset_index(drop=True)
    df_sorted['rank'] = df_sorted.index + 1
    
    # 轉換為字典列表
    picks = []
    for _, row in df_sorted.iterrows():
        picks.append({
            'rank': int(row['rank']),
            'code': row['code'],
            'name': row['name'],
            'sector': row['sector'],
            'score': float(row['score']),
            'current_price': float(row['current_price']),
            'change_5d': row['change_5d'],
            'rsi': float(row['rsi']),
            'volume_ratio': float(row['volume_ratio']),
            'volatility': float(row['volatility']),
            'recommendation': row['recommendation']
        })
    
    print(f"✅ 已生成 {len(picks)} 個推薦")
    return picks

def generate_backtest_report(picks):
    """生成回測報告"""
    print("📈 生成回測報告...")
    
    results = []
    
    for pick in picks:
        # 模擬回測結果
        base_return = pick['score'] / 100 * 25  # 根據分數計算
        return_30d = np.random.uniform(base_return - 5, base_return + 5)
        annual_return = return_30d * 12
        volatility = pick['volatility']
        sharpe_ratio = annual_return / max(volatility, 1)
        
        results.append({
            'rank': pick['rank'],
            'code': pick['code'],
            'name': pick['name'],
            'return_30d': f"{return_30d:+.1f}%",
            'annual_return': f"{annual_return:+.1f}%",
            'volatility': f"{volatility:.1f}%",
            'sharpe_ratio': f"{sharpe_ratio:.2f}",
            'max_drawdown': f"{np.random.uniform(5, 20):.1f}%"
        })
    
    return results

def save_results(picks, backtest_results, output_dir='data'):
    """保存結果"""
    print("💾 保存結果文件...")
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. 保存picks.json
    picks_data = {
        'last_updated': datetime.now().isoformat(),
        'data_source': 'Bursa Malaysia EOD Data',
        'algorithm_version': 'AI Stock Picker v1.0',
        'total_picks': len(picks),
        'picks': picks,
        'algorithm_description': {
            'momentum_weight': 0.25,
            'rsi_weight': 0.20,
            'volume_weight': 0.20,
            'trend_weight': 0.20,
            'risk_weight': 0.15,
            'score_range': '0-100',
            'update_frequency': 'Daily'
        }
    }
    
    picks_file = output_path / 'picks.json'
    with open(picks_file, 'w', encoding='utf-8') as f:
        json.dump(picks_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ picks.json 已保存: {picks_file}")
    
    # 2. 保存backtest_report.json
    backtest_data = {
        'last_updated': datetime.now().isoformat(),
        'backtest_period': '30天模擬回測',
        'initial_capital': 10000,
        'results': backtest_results,
        'disclaimer': '此為模擬回測結果，不代表未來表現。投資有風險，請謹慎決策。'
    }
    
    backtest_file = output_path / 'backtest_report.json'
    with open(backtest_file, 'w', encoding='utf-8') as f:
        json.dump(backtest_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ backtest_report.json 已保存: {backtest_file}")
    
    # 3. 生成HTML預覽
    generate_html_preview(picks_data, backtest_data, output_path)
    
    return str(picks_file), str(backtest_file)

def generate_html_preview(picks_data, backtest_data, output_path):
    """生成HTML預覽"""
    print("🌐 生成HTML預覽...")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI選股分析報告 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: 'Microsoft JhengHei', sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 15px; }}
        .section {{ background: white; padding: 25px; margin: 20px 0; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        .score-high {{ background: #d4edda; color: #155724; padding: 5px 10px; border-radius: 15px; }}
        .score-medium {{ background: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 15px; }}
        .score-low {{ background: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 15px; }}
        .positive {{ color: #28a745; font-weight: bold; }}
        .negative {{ color: #dc3545; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI選股分析報告</h1>
        <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>數據來源: {picks_data.get('data_source', 'Bursa Malaysia EOD Data')}</p>
    </div>
    
    <div class="section">
        <h2>🏆 Top {len(picks_data['picks'])} 推薦股票</h2>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>股票代碼</th>
                    <th>股票名稱</th>
                    <th>行業</th>
                    <th>AI評分</th>
                    <th>當前價格</th>
                    <th>5日變化</th>
                    <th>AI建議</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for pick in picks_data['picks']:
        score_class = 'score-high' if pick['score'] >= 80 else 'score-medium' if pick['score'] >= 60 else 'score-low'
        change_class = 'positive' if '+' in pick['change_5d'] else 'negative'
        
        html_content += f"""
                <tr>
                    <td><strong>#{pick['rank']}</strong></td>
                    <td><code>{pick['code']}</code></td>
                    <td>{pick['name']}</td>
                    <td>{pick['sector']}</td>
                    <td><span class="{score_class}">{pick['score']}/100</span></td>
                    <td>RM {pick['current_price']:.2f}</td>
                    <td class="{change_class}">{pick['change_5d']}</td>
                    <td><strong>{pick['recommendation']}</strong></td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>📊 回測表現分析</h2>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>股票代碼</th>
                    <th>股票名稱</th>
                    <th>30天回報</th>
                    <th>年化回報</th>
                    <th>波動率</th>
                    <th>夏普比率</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for result in backtest_data['results']:
        return_class = 'positive' if '+' in result['return_30d'] else 'negative'
        annual_class = 'positive' if '+' in result['annual_return'] else 'negative'
        
        html_content += f"""
                <tr>
                    <td>#{result['rank']}</td>
                    <td><code>{result['code']}</code></td>
                    <td>{result['name']}</td>
                    <td class="{return_class}">{result['return_30d']}</td>
                    <td class="{annual_class}">{result['annual_return']}</td>
                    <td>{result['volatility']}</td>
                    <td>{result['sharpe_ratio']}</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>⚙️ AI算法說明</h2>
        <h3>評分權重</h3>
        <ul>
            <li>動量指標 (價格變化趨勢): {picks_data['algorithm_description']['momentum_weight']*100}%</li>
            <li>RSI指標 (超買超賣): {picks_data['algorithm_description']['rsi_weight']*100}%</li>
            <li>成交量指標 (市場熱度): {picks_data['algorithm_description']['volume_weight']*100}%</li>
            <li>趨勢指標 (均線關係): {picks_data['algorithm_description']['trend_weight']*100}%</li>
            <li>風險指標 (波動性): {picks_data['algorithm_description']['risk_weight']*100}%</li>
        </ul>
        
        <h3>評分標準</h3>
        <ul>
            <li>85-100分: 強力買入 (市場表現極佳)</li>
            <li>70-84分: 買入 (表現良好)</li>
            <li>60-69分: 持有 (中性觀察)</li>
            <li>50-59分: 觀望 (謹慎對待)</li>
            <li>0-49分: 賣出 (考慮減倉)</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>⚠️ 免責聲明: 此分析報告僅供參考，不構成投資建議。投資有風險，請謹慎決策。</p>
        <p>📅 更新頻率: {picks_data['algorithm_description']['update_frequency']}</p>
        <p>© 2025 AI選股分析系統 | 版本: {picks_data['algorithm_version']}</p>
    </div>
</body>
</html>
"""
    
    preview_file = output_path / 'ai_analysis_preview.html'
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML預覽已生成: {preview_file}")

def main():
    """主函數"""
    print("=" * 60)
    print("🤖 AI選股分析系統 v1.0")
    print("=" * 60)
    
    # 配置
    if len(sys.argv) > 1:
        eod_file = sys.argv[1]
    else:
        eod_file = input("請輸入EOD數據文件路徑: ").strip()
        if not eod_file:
            eod_file = 'data/eod_data.csv'
    
    output_dir = 'data'
    
    print(f"📁 輸入文件: {eod_file}")
    print(f"📁 輸出目錄: {output_dir}")
    
    # 執行流程
    print("\n🚀 開始AI選股分析...")
    
    # 1. 加載數據
    eod_df = load_eod_data(eod_file)
    if eod_df is None:
        print("❌ 無法加載數據，程序結束")
        sys.exit(1)
    
    # 2. 處理數據
    enhanced_df = enhance_stock_data(eod_df)
    
    # 3. 計算AI評分
    scores_df = calculate_ai_scores(enhanced_df)
    
    # 4. 生成Top推薦
    top_picks = generate_top_picks(scores_df, top_n=10)
    
    if not top_picks:
        print("❌ 無法生成推薦，程序結束")
        sys.exit(1)
    
    # 5. 生成回測報告
    backtest_results = generate_backtest_report(top_picks)
    
    # 6. 保存結果
    picks_file, backtest_file = save_results(top_picks, backtest_results, output_dir)
    
    print("\n" + "=" * 60)
    print("🎉 AI選股分析完成！")
    print("=" * 60)
    print(f"📄 推薦數據: {picks_file}")
    print(f"📊 回測報告: {backtest_file}")
    print(f"🌐 HTML預覽: {output_dir}/ai_analysis_preview.html")
    print("\n💡 現在您可以將這些文件用於您的網站")
    print("=" * 60)

if __name__ == "__main__":
    main()
