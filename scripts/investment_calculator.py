#!/usr/bin/env python3
"""
Bursa Malaysia投资计算器 - Python版
功能：读取处理后的EOD数据，计算投资回报，生成详细分析报告
"""

import pandas as pd
import numpy as np
import sys
import os
import json
from datetime import datetime
from tabulate import tabulate
import argparse

# ============================================================================
# 费用配置（马来西亚交易所标准）
# ============================================================================
FEE_CONFIG = {
    # 经纪佣金
    'brokerage_rate': 0.0042,      # 0.42%
    'brokerage_min': 8.00,         # 最低 RM 8
    
    # 清算费
    'clearing_fee_rate': 0.0003,   # 0.03%
    'clearing_fee_cap': 200.00,    # 最高 RM 200
    
    # 印花税
    'stamp_duty_per_1000': 1.50,   # 每RM1000收RM1.50
    'stamp_duty_cap': 1000.00,     # 最高 RM 1000
    
    # 服务税（仅对经纪佣金）
    'service_tax_rate': 0.06,      # 6%
    
    # 投资目标
    'min_profit_target': 5.00,     # 最低利润目标 RM 5
}

# ============================================================================
# 核心计算函数
# ============================================================================

def load_stock_data(file_path):
    """
    加载处理后的股票数据
    支持CSV和JSON格式
    """
    print(f"📁 加载数据文件: {file_path}")
    
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            raise ValueError("不支持的文件格式，请使用CSV或JSON")
        
        print(f"✅ 加载成功: {len(df)} 行 × {len(df.columns)} 列")
        
        # 显示前几行
        print("\n📊 数据预览:")
        print(tabulate(df.head(5), headers='keys', tablefmt='pretty', showindex=False))
        
        return df
        
    except Exception as e:
        print(f"❌ 加载文件失败: {e}")
        return None

def display_stock_list(df):
    """
    显示股票列表，类似HTML版本
    """
    if df is None or len(df) == 0:
        print("❌ 没有股票数据可显示")
        return
    
    print("\n" + "="*80)
    print("🏆 AI推荐股票列表")
    print("="*80)
    
    # 检查是否有必要的列
    if 'Code' not in df.columns:
        print("⚠  警告: 数据中没有'Code'列，使用第一列作为股票代码")
        code_col = df.columns[0]
    else:
        code_col = 'Code'
    
    # 为每只股票生成详细显示
    for idx, row in df.iterrows():
        if idx >= 20:  # 只显示前20只
            break
        
        # 提取基本信息
        code = str(row[code_col]) if code_col in row else "N/A"
        name = row.get('Stock', row.get('Name', '未知'))
        
        # 提取价格信息
        price = 0.0
        for price_col in ['Last', 'Current_Price', 'Price', 'current_price']:
            if price_col in row and pd.notna(row[price_col]):
                price = float(row[price_col])
                break
        
        # 提取涨跌幅
        change_pct = 0.0
        for change_col in ['Chg', 'Change', 'daily_change', 'Change%']:
            if change_col in row and pd.notna(row[change_col]):
                try:
                    change_pct = float(row[change_col])
                except:
                    change_pct = 0.0
                break
        
        # 提取AI评分
        ai_score = 0
        for score_col in ['score', 'Score', 'potential_score', 'AI_Score']:
            if score_col in row and pd.notna(row[score_col]):
                try:
                    ai_score = float(row[score_col])
                except:
                    ai_score = 0
                break
        
        # 判断股票类型（Warrant还是普通股）
        instrument_type = "Stock"
        for type_col in ['instrument_type', 'Instrument_Type', 'Type']:
            if type_col in row and pd.notna(row[type_col]):
                inst_type = str(row[type_col]).lower()
                if 'warrant' in inst_type or 'w' in inst_type:
                    instrument_type = "Warrant"
                break
        
        # 判断风险等级
        risk_level = "中"
        for risk_col in ['risk_level', 'Risk_Level', 'Risk']:
            if risk_col in row and pd.notna(row[risk_col]):
                risk_text = str(row[risk_col]).lower()
                if '高' in risk_text or 'high' in risk_text:
                    risk_level = "高"
                elif '低' in risk_text or 'low' in risk_text:
                    risk_level = "低"
                break
        
        # 生成显示行
        rank = idx + 1
        price_str = f"RM {price:.3f}"
        change_str = f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%"
        change_color = "🟢" if change_pct >= 0 else "🔴"
        
        # 类型图标
        type_icon = "🔵" if instrument_type == "Stock" else "🟣"
        
        print(f"\n#{rank:2d} {type_icon} {code:8s} - {name[:30]:30s}")
        print(f"   价格: {price_str:10s} {change_color} {change_str:10s}")
        print(f"   AI评分: {ai_score:4.0f}/100 | 风险: {risk_level:2s} | 类型: {instrument_type:8s}")
        
        # 显示推荐原因（如果有）
        reason_cols = ['potential_reasons', 'Recommendation', 'Reasons']
        for reason_col in reason_cols:
            if reason_col in row and pd.notna(row[reason_col]) and str(row[reason_col]).strip():
                reason = str(row[reason_col])[:50]
                print(f"   💡 {reason}")
                break

def select_stock_interactive(df):
    """
    交互式选择股票
    """
    if df is None or len(df) == 0:
        print("❌ 没有股票数据")
        return None
    
    # 显示选择菜单
    print("\n" + "="*80)
    print("🎯 请选择要计算的股票")
    print("="*80)
    
    # 创建简化的选择列表
    stock_list = []
    
    for idx, row in df.iterrows():
        if idx >= 20:  # 只显示前20只
            break
        
        # 提取基本信息
        code_col = 'Code' if 'Code' in df.columns else df.columns[0]
        code = str(row[code_col]) if code_col in row else f"Stock_{idx+1}"
        
        name = row.get('Stock', row.get('Name', '未知股票'))
        name_display = name[:20] if len(name) > 20 else name
        
        # 获取价格
        price = 0.0
        for price_col in ['Last', 'Current_Price', 'Price']:
            if price_col in row and pd.notna(row[price_col]):
                price = float(row[price_col])
                break
        
        stock_list.append({
            'index': idx + 1,
            'code': code,
            'name': name_display,
            'price': price
        })
    
    # 显示选择菜单
    for stock in stock_list:
        print(f"{stock['index']:2d}. {stock['code']:8s} - {stock['name']:20s} (RM {stock['price']:.3f})")
    
    print("\n" + "-"*80)
    
    # 获取用户选择
    while True:
        try:
            choice = input("请选择股票编号 (1-20), 或输入'q'退出: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(stock_list):
                selected_stock = stock_list[choice_idx]
                original_idx = selected_stock['index'] - 1
                print(f"\n✅ 已选择: {selected_stock['code']} - {selected_stock['name']}")
                return df.iloc[original_idx]
            else:
                print("❌ 无效的选择，请重试")
                
        except ValueError:
            print("❌ 请输入有效的数字")
        except Exception as e:
            print(f"❌ 选择出错: {e}")

def get_user_input():
    """
    获取用户输入的投资参数
    """
    print("\n" + "="*80)
    print("💰 投资参数设置")
    print("="*80)
    
    inputs = {}
    
    # 获取买入价
    while True:
        try:
            buy_price = input("请输入买入价 (例如: 0.500): ").strip()
            if not buy_price:
                print("⚠  使用当前股价作为买入价")
                inputs['buy_price'] = None  # 稍后从股票数据获取
                break
            
            buy_price = float(buy_price)
            if buy_price > 0:
                inputs['buy_price'] = buy_price
                break
            else:
                print("❌ 买入价必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    # 获取卖出价
    while True:
        try:
            sell_price = input("请输入目标卖出价 (例如: 0.600): ").strip()
            if not sell_price:
                print("⚠  未设置卖出价，将计算建议卖出价")
                inputs['sell_price'] = None
                break
            
            sell_price = float(sell_price)
            if sell_price > 0:
                inputs['sell_price'] = sell_price
                break
            else:
                print("❌ 卖出价必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    # 获取购买股数（以100股为单位）
    while True:
        try:
            units = input("请输入购买股数 (单位: 100股，例如: 10 = 1000股): ").strip()
            if not units:
                units = "10"
            
            units = int(units)
            if 1 <= units <= 1000:
                inputs['share_units'] = units
                inputs['total_shares'] = units * 100  # 转换为总股数
                break
            else:
                print("❌ 股数必须在1-1000之间 (100-100000股)")
        except ValueError:
            print("❌ 请输入有效的整数")
    
    # 获取自定义费用（可选）
    print("\n💡 费用设置 (按Enter使用默认值)")
    
    fees = FEE_CONFIG.copy()
    
    for fee_name, default_value in fees.items():
        if fee_name in ['brokerage_rate', 'clearing_fee_rate', 'service_tax_rate']:
            # 百分比类型
            display_value = f"{default_value * 100:.2f}%"
            prompt = f"{fee_name.replace('_', ' ').title()} [{display_value}]: "
        else:
            # 金额类型
            display_value = f"RM {default_value:.2f}"
            prompt = f"{fee_name.replace('_', ' ').title()} [{display_value}]: "
        
        user_input = input(prompt).strip()
        
        if user_input:
            try:
                if fee_name in ['brokerage_rate', 'clearing_fee_rate', 'service_tax_rate']:
                    # 百分比输入，去除%符号
                    if '%' in user_input:
                        user_input = user_input.replace('%', '')
                    new_value = float(user_input) / 100
                else:
                    new_value = float(user_input)
                
                fees[fee_name] = new_value
                print(f"   ✅ 已更新为: {display_value}")
            except ValueError:
                print(f"   ⚠  使用默认值: {display_value}")
    
    inputs['fees'] = fees
    
    return inputs

def calculate_investment_return(stock_data, user_inputs):
    """
    计算投资回报（核心计算逻辑）
    """
    print("\n" + "="*80)
    print("🧮 计算投资回报")
    print("="*80)
    
    # 获取价格
    if user_inputs['buy_price'] is None:
        # 从股票数据获取当前价格
        buy_price = 0.0
        for price_col in ['Last', 'Current_Price', 'Price']:
            if price_col in stock_data and pd.notna(stock_data[price_col]):
                buy_price = float(stock_data[price_col])
                break
    else:
        buy_price = user_inputs['buy_price']
    
    if user_inputs['sell_price'] is None:
        # 计算建议卖出价（基于AI潜力评分）
        ai_score = 0
        for score_col in ['score', 'Score', 'potential_score']:
            if score_col in stock_data and pd.notna(stock_data[score_col]):
                ai_score = float(stock_data[score_col])
                break
        
        # 根据AI评分计算建议涨幅
        if ai_score >= 80:
            target_increase = 0.15  # 15%
        elif ai_score >= 70:
            target_increase = 0.10  # 10%
        elif ai_score >= 60:
            target_increase = 0.07  # 7%
        else:
            target_increase = 0.05  # 5%
        
        sell_price = buy_price * (1 + target_increase)
        print(f"💡 基于AI评分 {ai_score:.0f}，建议目标涨幅: {target_increase*100:.1f}%")
    else:
        sell_price = user_inputs['sell_price']
    
    # 获取股数和费用
    share_units = user_inputs['share_units']
    total_shares = user_inputs['total_shares']
    fees = user_inputs['fees']
    
    # 计算买入和卖出总额
    buy_total = buy_price * total_shares
    sell_total = sell_price * total_shares
    
    print(f"\n📊 基础计算:")
    print(f"   买入价: RM {buy_price:.3f} × {total_shares:,} 股 = RM {buy_total:.2f}")
    print(f"   卖出价: RM {sell_price:.3f} × {total_shares:,} 股 = RM {sell_total:.2f}")
    print(f"   毛利润: RM {sell_total - buy_total:.2f}")
    
    # 计算各项费用
    print(f"\n💸 费用明细:")
    
    # 1. 经纪佣金
    buy_brokerage = max(buy_total * fees['brokerage_rate'], fees['brokerage_min'])
    sell_brokerage = max(sell_total * fees['brokerage_rate'], fees['brokerage_min'])
    total_brokerage = buy_brokerage + sell_brokerage
    
    print(f"   经纪佣金: RM {total_brokerage:.2f}")
    print(f"     • 买入: RM {buy_brokerage:.2f} (RM {buy_total:.2f} × {fees['brokerage_rate']*100:.2f}%, 最低RM {fees['brokerage_min']:.2f})")
    print(f"     • 卖出: RM {sell_brokerage:.2f} (RM {sell_total:.2f} × {fees['brokerage_rate']*100:.2f}%, 最低RM {fees['brokerage_min']:.2f})")
    
    # 2. 清算费
    buy_clearing = min(buy_total * fees['clearing_fee_rate'], fees['clearing_fee_cap'])
    sell_clearing = min(sell_total * fees['clearing_fee_rate'], fees['clearing_fee_cap'])
    total_clearing = buy_clearing + sell_clearing
    
    print(f"   清算费: RM {total_clearing:.2f}")
    print(f"     • 买入: RM {buy_clearing:.2f} (RM {buy_total:.2f} × {fees['clearing_fee_rate']*100:.3f}%, 最高RM {fees['clearing_fee_cap']:.2f})")
    print(f"     • 卖出: RM {sell_clearing:.2f} (RM {sell_total:.2f} × {fees['clearing_fee_rate']*100:.3f}%, 最高RM {fees['clearing_fee_cap']:.2f})")
    
    # 3. 印花税
    buy_stamp = min(np.ceil(buy_total / 1000) * fees['stamp_duty_per_1000'], fees['stamp_duty_cap'])
    sell_stamp = min(np.ceil(sell_total / 1000) * fees['stamp_duty_per_1000'], fees['stamp_duty_cap'])
    total_stamp = buy_stamp + sell_stamp
    
    print(f"   印花税: RM {total_stamp:.2f}")
    print(f"     • 买入: RM {buy_stamp:.2f} (每RM1000收RM{fees['stamp_duty_per_1000']:.2f}, 最高RM {fees['stamp_duty_cap']:.2f})")
    print(f"     • 卖出: RM {sell_stamp:.2f} (每RM1000收RM{fees['stamp_duty_per_1000']:.2f}, 最高RM {fees['stamp_duty_cap']:.2f})")
    
    # 4. 服务税
    service_tax = total_brokerage * fees['service_tax_rate']
    print(f"   服务税: RM {service_tax:.2f} (经纪佣金 × {fees['service_tax_rate']*100:.0f}%)")
    
    # 总费用
    total_fees = total_brokerage + total_clearing + total_stamp + service_tax
    print(f"   📋 总费用: RM {total_fees:.2f}")
    
    # 净回报
    net_profit = sell_total - buy_total - total_fees
    profit_percentage = (net_profit / buy_total) * 100 if buy_total > 0 else 0
    
    # 计算盈亏平衡价格
    buy_cost_per_share = (buy_total + buy_brokerage + buy_clearing + buy_stamp + (service_tax / 2)) / total_shares
    break_even_price = (buy_cost_per_share * total_shares + sell_brokerage + sell_clearing + sell_stamp + (service_tax / 2)) / total_shares
    
    # 计算达到目标利润的价格
    target_profit_price = (buy_cost_per_share * total_shares + sell_brokerage + sell_clearing + sell_stamp + (service_tax / 2) + fees['min_profit_target']) / total_shares
    
    # 返回计算结果
    results = {
        'buy_price': buy_price,
        'sell_price': sell_price,
        'total_shares': total_shares,
        'buy_total': buy_total,
        'sell_total': sell_total,
        'gross_profit': sell_total - buy_total,
        'fees_detail': {
            'brokerage': total_brokerage,
            'clearing': total_clearing,
            'stamp_duty': total_stamp,
            'service_tax': service_tax,
            'total': total_fees
        },
        'net_profit': net_profit,
        'profit_percentage': profit_percentage,
        'break_even_price': break_even_price,
        'target_profit_price': target_profit_price,
        'min_profit_target': fees['min_profit_target']
    }
    
    return results

def display_results(stock_data, results):
    """
    显示计算结果
    """
    print("\n" + "="*80)
    print("🎉 投资回报分析结果")
    print("="*80)
    
    # 股票基本信息
    code_col = 'Code' if 'Code' in stock_data.index else stock_data.index[0] if isinstance(stock_data, pd.Series) else 'N/A'
    code = str(stock_data[code_col]) if code_col in stock_data else 'N/A'
    
    name = stock_data.get('Stock', stock_data.get('Name', '未知股票'))
    
    print(f"\n📈 股票: {code} - {name}")
    print(f"   买入价: RM {results['buy_price']:.3f}")
    print(f"   卖出价: RM {results['sell_price']:.3f}")
    print(f"   总股数: {results['total_shares']:,} 股")
    
    print(f"\n💰 金额汇总:")
    print(f"   买入总额: RM {results['buy_total']:,.2f}")
    print(f"   卖出总额: RM {results['sell_total']:,.2f}")
    print(f"   毛利潤: RM {results['gross_profit']:,.2f}")
    
    print(f"\n💸 费用扣除:")
    fees = results['fees_detail']
    print(f"   经纪佣金: RM {fees['brokerage']:,.2f}")
    print(f"   清算费: RM {fees['clearing']:,.2f}")
    print(f"   印花税: RM {fees['stamp_duty']:,.2f}")
    print(f"   服务税: RM {fees['service_tax']:,.2f}")
    print(f"   ────────────────────")
    print(f"   总费用: RM {fees['total']:,.2f}")
    
    print(f"\n📊 最终结果:")
    
    if results['net_profit'] >= 0:
        profit_emoji = "✅"
        profit_color = "🟢"
    else:
        profit_emoji = "❌"
        profit_color = "🔴"
    
    print(f"   {profit_emoji} 净回报: {profit_color} RM {results['net_profit']:+,.2f}")
    print(f"   📈 回报率: {profit_color} {results['profit_percentage']:+.2f}%")
    
    # 检查是否达到最低利润目标
    if results['net_profit'] >= results['min_profit_target']:
        print(f"   🎯 达到最低利润目标: RM {results['min_profit_target']:.2f} ✓")
    else:
        print(f"   ⚠  未达到最低利润目标: RM {results['min_profit_target']:.2f}")
        print(f"     当前利润: RM {results['net_profit']:.2f}")
    
    print(f"\n⚖️  关键价格点:")
    print(f"   盈亏平衡价: RM {results['break_even_price']:.3f}")
    print(f"   目标利润价: RM {results['target_profit_price']:.3f}")
    
    # 提供建议
    print(f"\n💡 投资建议:")
    
    if results['net_profit'] > results['min_profit_target'] * 2:
        print("   🚀 强烈建议：预期回报良好，远超最低目标")
    elif results['net_profit'] >= results['min_profit_target']:
        print("   👍 可以考虑：达到最低利润目标")
    elif results['net_profit'] > 0:
        print("   🤔 谨慎考虑：虽有盈利但未达最低目标")
    else:
        print("   ⚠️  不建议：预期亏损")
    
    # 显示费用占比
    print(f"\n📋 费用结构分析:")
    if results['buy_total'] > 0:
        fee_percentage = (fees['total'] / results['buy_total']) * 100
        print(f"   费用占总投资的 {fee_percentage:.2f}%")
        
        profit_after_fees = (results['net_profit'] / results['buy_total']) * 100
        print(f"   扣费后净回报率: {profit_after_fees:+.2f}%")

def save_results_to_file(stock_data, results, output_file=None):
    """
    保存计算结果到文件
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"investment_calculation_{timestamp}.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("Bursa Malaysia投资计算器 - 计算结果\n")
            f.write("="*80 + "\n\n")
            
            # 股票信息
            code = str(stock_data.get('Code', 'N/A'))
            name = stock_data.get('Stock', stock_data.get('Name', '未知股票'))
            
            f.write(f"股票: {code} - {name}\n")
            f.write(f"计算时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("投资参数:\n")
            f.write(f"   买入价: RM {results['buy_price']:.3f}\n")
            f.write(f"   卖出价: RM {results['sell_price']:.3f}\n")
            f.write(f"   总股数: {results['total_shares']:,} 股\n")
            f.write(f"   买入总额: RM {results['buy_total']:,.2f}\n")
            f.write(f"   卖出总额: RM {results['sell_total']:,.2f}\n\n")
            
            f.write("费用明细:\n")
            fees = results['fees_detail']
            f.write(f"   经纪佣金: RM {fees['brokerage']:,.2f}\n")
            f.write(f"   清算费: RM {fees['clearing']:,.2f}\n")
            f.write(f"   印花税: RM {fees['stamp_duty']:,.2f}\n")
            f.write(f"   服务税: RM {fees['service_tax']:,.2f}\n")
            f.write(f"   总费用: RM {fees['total']:,.2f}\n\n")
            
            f.write("计算结果:\n")
            f.write(f"   净回报: RM {results['net_profit']:+,.2f}\n")
            f.write(f"   回报率: {results['profit_percentage']:+.2f}%\n")
            f.write(f"   盈亏平衡价: RM {results['break_even_price']:.3f}\n")
            f.write(f"   目标利润价: RM {results['target_profit_price']:.3f}\n\n")
            
            if results['net_profit'] >= results['min_profit_target']:
                f.write("投资建议: ✓ 达到最低利润目标，可以考虑投资\n")
            else:
                f.write(f"投资建议: ⚠ 未达到最低利润目标 (需RM {results['min_profit_target']:.2f})\n")
        
        print(f"💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"⚠  无法保存结果到文件: {e}")

# ============================================================================
# 主程序
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Bursa Malaysia投资计算器')
    parser.add_argument('data_file', nargs='?', help='股票数据文件 (CSV或JSON)')
    parser.add_argument('-o', '--output', help='输出结果文件')
    parser.add_argument('--auto', action='store_true', help='自动模式（使用默认参数）')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🏦 Bursa Malaysia投资计算器 - Python版")
    print("="*80)
    
    # 1. 加载数据
    if args.data_file:
        data_file = args.data_file
    else:
        # 如果没有提供文件，尝试自动查找
        print("🔍 自动查找股票数据文件...")
        
        # 查找最新处理过的CSV文件
        import glob
        csv_files = glob.glob("*_processed_*.csv") + glob.glob("*_reordered*.csv")
        
        if csv_files:
            # 按修改时间排序
            csv_files.sort(key=os.path.getmtime, reverse=True)
            data_file = csv_files[0]
            print(f"📁 找到最新文件: {data_file}")
        else:
            print("❌ 未找到股票数据文件")
            print("💡 请使用: python investment_calculator.py 数据文件.csv")
            return
    
    df = load_stock_data(data_file)
    
    if df is None or len(df) == 0:
        print("❌ 无法加载股票数据，程序退出")
        return
    
    # 2. 显示股票列表
    display_stock_list(df)
    
    # 3. 选择股票
    if args.auto:
        # 自动模式：选择第一只股票
        print("\n🤖 自动模式：选择第一只股票")
        selected_stock = df.iloc[0]
    else:
        selected_stock = select_stock_interactive(df)
    
    if selected_stock is None:
        print("👋 用户取消，程序退出")
        return
    
    # 4. 获取投资参数
    if args.auto:
        # 自动模式使用默认参数
        print("\n🤖 自动模式：使用默认参数")
        user_inputs = {
            'buy_price': None,  # 使用当前股价
            'sell_price': None,  # 自动计算
            'share_units': 10,
            'total_shares': 1000,
            'fees': FEE_CONFIG
        }
    else:
        user_inputs = get_user_input()
    
    # 5. 计算投资回报
    results = calculate_investment_return(selected_stock, user_inputs)
    
    # 6. 显示结果
    display_results(selected_stock, results)
    
    # 7. 保存结果
    if args.output or not args.auto:
        save_option = input("\n💾 是否保存结果到文件? (y/n, 默认y): ").strip().lower()
        if save_option in ['y', 'yes', '']:
            output_file = args.output if args.output else None
            save_results_to_file(selected_stock, results, output_file)
    
    print("\n" + "="*80)
    print("✅ 投资计算完成！")
    print("="*80)

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
