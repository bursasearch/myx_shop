#!/usr/bin/env python3
"""
从EOD CSV生成HTML所需的JSON文件
为 retail-inv.html 提供实时数据
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import glob
from datetime import datetime, timedelta
import re

def load_eod_csv(csv_path):
    """
    加载经纪商提供的EOD CSV文件
    支持多种格式：Excel导出、CSV、TSV等
    """
    print(f"📁 加载EOD文件: {csv_path}")
    
    try:
        # 尝试不同的编码
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # 读取CSV文件
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✅ 使用编码: {encoding}")
                print(f"📊 数据形状: {df.shape}")
                
                # 显示列名
                print(f"📋 列名: {list(df.columns)}")
                
                return df
            except UnicodeDecodeError:
                continue
        
        # 如果所有编码都失败，尝试不带编码
        df = pd.read_csv(csv_path)
        return df
        
    except Exception as e:
        print(f"❌ 加载CSV失败: {e}")
        
        # 尝试其他格式
        try:
            # 尝试Excel格式
            df = pd.read_excel(csv_path)
            print("✅ 成功读取Excel文件")
            return df
        except:
            print("❌ 无法读取文件，请检查格式")
            return None

def detect_and_clean_columns(df):
    """
    自动检测和清理列名
    处理经纪商CSV的各种列名格式
    """
    if df is None or len(df) == 0:
        return None
    
    # 清理列名：去除空格和特殊字符
    df.columns = [str(col).strip().replace('\ufeff', '') for col in df.columns]
    
    print("\n🔧 列名清理后:")
    print(f"  列名: {list(df.columns)}")
    
    # 查找关键列
    column_mapping = {}
    
    # Code/股票代码列
    code_patterns = ['Code', '股票代码', '代码', 'Symbol', 'Ticker', '代号']
    for pattern in code_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['code'] = col
                print(f"  ✅ 找到代码列: {col} → code")
                break
        if 'code' in column_mapping:
            break
    
    # Name/股票名称列
    name_patterns = ['Stock', '股票', '名称', 'Name', '公司名称']
    for pattern in name_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['name'] = col
                print(f"  ✅ 找到名称列: {col} → name")
                break
        if 'name' in column_mapping:
            break
    
    # Last Price/最新价列
    price_patterns = ['Last', '最新价', '现价', '当前价', '收盘价', '成交价']
    for pattern in price_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['last_price'] = col
                print(f"  ✅ 找到价格列: {col} → last_price")
                break
        if 'last_price' in column_mapping:
            break
    
    # Change/涨跌幅列
    change_patterns = ['Chg', '涨跌', '变化', 'Change', '涨跌幅', 'Chg%']
    for pattern in change_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['change_percent'] = col
                print(f"  ✅ 找到涨跌幅列: {col} → change_percent")
                break
        if 'change_percent' in column_mapping:
            break
    
    # Volume/成交量列
    volume_patterns = ['Vol', '成交量', '交易量', 'Volume']
    for pattern in volume_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['volume'] = col
                print(f"  ✅ 找到成交量列: {col} → volume")
                break
        if 'volume' in column_mapping:
            break
    
    # Sector/行业列
    sector_patterns = ['Sector', '行业', '板块', 'Industry']
    for pattern in sector_patterns:
        for col in df.columns:
            if pattern in col:
                column_mapping['sector'] = col
                print(f"  ✅ 找到行业列: {col} → sector")
                break
        if 'sector' in column_mapping:
            break
    
    return column_mapping

def create_ai_picks(df, column_mapping, top_n=20):
    """
    基于EOD数据创建AI选股列表
    模拟AI评分逻辑
    """
    print(f"\n🤖 生成AI选股推荐 (前{top_n}名)...")
    
    if df is None or len(df) == 0:
        print("❌ 没有数据生成选股")
        return []
    
    picks = []
    
    # 确保有必要的列
    required_cols = ['code', 'name', 'last_price', 'change_percent']
    missing_cols = [col for col in required_cols if col not in column_mapping]
    
    if missing_cols:
        print(f"⚠  缺少必要列: {missing_cols}")
        return []
    
    # 提取数据
    for idx, row in df.iterrows():
        if len(picks) >= top_n:
            break
        
        try:
            # 获取基本数据
            code = str(row[column_mapping['code']]) if column_mapping['code'] in row else f"STOCK_{idx+1:04d}"
            name = str(row[column_mapping['name']]) if column_mapping['name'] in row else f"股票_{idx+1}"
            
            # 获取价格数据
            last_price = 0.0
            if column_mapping['last_price'] in row and pd.notna(row[column_mapping['last_price']]):
                try:
                    last_price = float(row[column_mapping['last_price']])
                except:
                    last_price = 0.0
            
            # 获取涨跌幅
            change_percent = 0.0
            if column_mapping['change_percent'] in row and pd.notna(row[column_mapping['change_percent']]):
                try:
                    change_val = str(row[column_mapping['change_percent']])
                    # 清理百分比符号
                    change_val = change_val.replace('%', '').strip()
                    change_percent = float(change_val)
                except:
                    change_percent = 0.0
            
            # 获取成交量
            volume = 0
            if 'volume' in column_mapping and column_mapping['volume'] in row and pd.notna(row[column_mapping['volume']]):
                try:
                    vol_str = str(row[column_mapping['volume']])
                    # 清理千位分隔符
                    vol_str = vol_str.replace(',', '').replace(' ', '')
                    volume = int(float(vol_str)) if vol_str.replace('.', '').isdigit() else 0
                except:
                    volume = 0
            
            # 获取行业
            sector = ""
            if 'sector' in column_mapping and column_mapping['sector'] in row and pd.notna(row[column_mapping['sector']]):
                sector = str(row[column_mapping['sector']])
            
            # AI评分逻辑
            score = 50  # 基础分
            
            # 基于涨跌幅评分
            if change_percent > 5:
                score += 15
            elif change_percent > 2:
                score += 10
            elif change_percent > 0:
                score += 5
            elif change_percent < -5:
                score -= 10
            
            # 基于成交量评分
            if volume > 1000000:
                score += 10
            elif volume > 100000:
                score += 5
            elif volume < 10000:
                score -= 5
            
            # 基于价格评分（低价股可能更有潜力）
            if 0.05 < last_price < 1.00:
                score += 5
            elif last_price < 0.05:
                score += 10  # 极低价可能有高波动性
            
            # 确保分数在0-100之间
            score = max(0, min(100, score))
            
            # 潜力评分（基于AI评分和涨跌幅）
            potential_score = score + (change_percent * 0.5)
            potential_score = max(0, min(100, potential_score))
            
            # 判断股票类型
            instrument_type = "Stock"
            if isinstance(code, str):
                if '-' in code or code[-1].isalpha():
                    instrument_type = "Warrant"
            
            # 风险等级
            risk_level = "中"
            if change_percent > 20:
                risk_level = "高"
            elif change_percent < -10:
                risk_level = "高"
            elif abs(change_percent) < 2:
                risk_level = "低"
            
            # 推荐理由
            potential_reasons = []
            if change_percent > 2:
                potential_reasons.append("价格上涨趋势明显")
            if volume > 100000:
                potential_reasons.append("成交量活跃")
            if score > 70:
                potential_reasons.append("AI评分较高")
            if last_price < 0.50:
                potential_reasons.append("低价股反弹潜力大")
            
            if not potential_reasons:
                potential_reasons.append("综合评估中性")
            
            # 推荐建议
            recommendation = "👍買入"
            if score >= 80:
                recommendation = "🔥強烈買入"
            elif score >= 70:
                recommendation = "👍買入"
            elif score >= 60:
                recommendation = "🤔考慮買入"
            elif score >= 50:
                recommendation = "⚖️中性"
            elif score >= 40:
                recommendation = "⚠️考慮賣出"
            else:
                recommendation = "🚫賣出"
            
            if instrument_type == "Warrant":
                recommendation += "（Warrant）"
            
            # 添加到选股列表
            pick = {
                "rank": len(picks) + 1,
                "code": code,
                "name": name,
                "instrument_type": instrument_type,
                "sector": sector,
                "current_price": round(last_price, 3),
                "daily_change": round(change_percent, 2),
                "score": round(score, 1),
                "potential_score": int(potential_score),
                "potential_reasons": "，".join(potential_reasons[:2]),
                "recommendation": recommendation,
                "risk_level": risk_level,
                "rsi": round(50 + (change_percent * 0.5), 1),  # 模拟RSI
                "volume": volume,
                "status": "推薦" if score >= 60 else "觀望"
            }
            
            picks.append(pick)
            
        except Exception as e:
            print(f"⚠  处理第{idx+1}行数据时出错: {e}")
            continue
    
    # 按潜力评分排序
    picks.sort(key=lambda x: x['potential_score'], reverse=True)
    
    # 更新排名
    for i, pick in enumerate(picks):
        pick['rank'] = i + 1
    
    print(f"✅ 成功生成 {len(picks)} 个AI选股推荐")
    return picks

def create_latest_price_json(df, column_mapping):
    """
    创建latest_price.json - 所有股票的最新价格
    """
    print(f"\n📈 生成最新股价数据...")
    
    if df is None or len(df) == 0:
        print("❌ 没有数据生成股价")
        return []
    
    stocks_list = []
    
    for idx, row in df.iterrows():
        try:
            # 获取股票代码
            code = ""
            if 'code' in column_mapping and column_mapping['code'] in row and pd.notna(row[column_mapping['code']]):
                code = str(row[column_mapping['code']])
            else:
                code = f"STOCK_{idx+1:04d}"
            
            # 获取股票名称
            name = ""
            if 'name' in column_mapping and column_mapping['name'] in row and pd.notna(row[column_mapping['name']]):
                name = str(row[column_mapping['name']])
            else:
                name = f"股票_{idx+1}"
            
            # 获取最新价格
            last_price = 0.0
            if 'last_price' in column_mapping and column_mapping['last_price'] in row and pd.notna(row[column_mapping['last_price']]):
                try:
                    last_price = float(row[column_mapping['last_price']])
                except:
                    last_price = 0.0
            
            # 获取涨跌
            change = 0.0
            change_percent = 0.0
            if 'change_percent' in column_mapping and column_mapping['change_percent'] in row and pd.notna(row[column_mapping['change_percent']]):
                try:
                    change_val = str(row[column_mapping['change_percent']])
                    change_val = change_val.replace('%', '').strip()
                    change_percent = float(change_val)
                    change = last_price * (change_percent / 100)  # 计算涨跌金额
                except:
                    change_percent = 0.0
                    change = 0.0
            
            # 获取成交量
            volume = 0
            if 'volume' in column_mapping and column_mapping['volume'] in row and pd.notna(row[column_mapping['volume']]):
                try:
                    vol_str = str(row[column_mapping['volume']])
                    vol_str = vol_str.replace(',', '').replace(' ', '')
                    volume = int(float(vol_str)) if vol_str.replace('.', '').isdigit() else 0
                except:
                    volume = 0
            
            # 获取行业
            sector = "Unknown"
            if 'sector' in column_mapping and column_mapping['sector'] in row and pd.notna(row[column_mapping['sector']]):
                sector = str(row[column_mapping['sector']])
            
            # 其他技术指标（模拟）
            open_price = last_price * 0.99  # 模拟开盘价
            high_price = last_price * 1.02  # 模拟最高价
            low_price = last_price * 0.98   # 模拟最低价
            
            stock_data = {
                'code': code,
                'name': name,
                'last_price': round(last_price, 3),
                'change': round(change, 3),
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'sector': sector,
                'open': round(open_price, 3),
                'high': round(high_price, 3),
                'low': round(low_price, 3),
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            
            stocks_list.append(stock_data)
            
        except Exception as e:
            print(f"⚠  处理股价数据第{idx+1}行时出错: {e}")
            continue
    
    print(f"✅ 成功生成 {len(stocks_list)} 个股价数据")
    return stocks_list

def save_json(data, filename, output_dir="."):
    """
    保存JSON文件，确保中文正确显示
    """
    output_path = os.path.join(output_dir, filename)
    
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存到: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ 保存JSON失败 {filename}: {e}")
        return False

def main():
    """主函数"""
    print("="*70)
    print("🏦 EOD CSV 转 JSON 生成器")
    print("为 retail-inv.html 提供实时数据")
    print("="*70)
    
    # 参数处理
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # 自动查找最新的EOD CSV文件
        print("\n🔍 自动查找最新的EOD CSV文件...")
        
        # 常见的EOD文件位置
        search_paths = [
            "/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/",
            "/storage/emulated/0/Download/",
            "./",
            "."
        ]
        
        csv_files = []
        for path in search_paths:
            if os.path.exists(path):
                found = glob.glob(os.path.join(path, "*.csv"))
                csv_files.extend(found)
        
        if not csv_files:
            print("❌ 未找到CSV文件")
            print("💡 使用方法: python generate_json_from_eod.py 文件.csv")
            return
        
        # 按修改时间排序（最新的在前）
        csv_files.sort(key=os.path.getmtime, reverse=True)
        csv_path = csv_files[0]
    
    print(f"\n📁 使用文件: {csv_path}")
    
    # 1. 加载CSV文件
    df = load_eod_csv(csv_path)
    
    if df is None or len(df) == 0:
        print("❌ 无法加载数据，程序退出")
        return
    
    # 2. 检测和清理列
    column_mapping = detect_and_clean_columns(df)
    
    if not column_mapping:
        print("❌ 无法识别数据列，程序退出")
        return
    
    # 3. 生成AI选股数据
    picks_data = create_ai_picks(df, column_mapping, top_n=20)
    
    if picks_data:
        # 创建完整的picks_latest.json结构
        picks_json = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source": os.path.basename(csv_path),
            "total_picks": len(picks_data),
            "picks": picks_data
        }
        
        # 保存picks_latest.json
        save_json(picks_json, "picks_latest.json", ".")
        
        # 同时保存一个带日期的版本
        date_str = datetime.now().strftime('%Y%m%d')
        history_dir = "history"
        save_json(picks_json, f"picks_{date_str}.json", history_dir)
    
    # 4. 生成最新股价数据
    price_data = create_latest_price_json(df, column_mapping)
    
    if price_data:
        # 创建完整的latest_price.json结构
        price_json = {
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data_date": datetime.now().strftime('%Y-%m-%d'),
            "total_stocks": len(price_data),
            "market": "Bursa Malaysia",
            "source": "Broker EOD Data",
            "stocks": price_data
        }
        
        # 保存latest_price.json
        save_json(price_json, "latest_price.json", ".")
    
    # 5. 生成HTML数据文件（简化版，供HTML直接使用）
    html_data = {
        "ai_picks": picks_data[:10] if picks_data else [],
        "latest_prices": price_data[:50] if price_data else [],
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data_source": os.path.basename(csv_path)
    }
    
    save_json(html_data, "data.json", ".")
    
    print("\n" + "="*70)
    print("🎉 JSON文件生成完成！")
    print("="*70)
    print(f"📊 输入数据: {len(df)} 行")
    print(f"🎯 AI选股: {len(picks_data)} 个推荐")
    print(f"📈 股价数据: {len(price_data)} 只股票")
    print("\n📁 生成的文件:")
    print("  • picks_latest.json     - AI选股推荐")
    print("  • latest_price.json     - 最新股价")
    print("  • history/picks_YYYYMMDD.json - 历史选股")
    print("  • data.json             - HTML页面数据")
    print("\n🌐 现在可以直接使用 retail-inv.html 了！")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
