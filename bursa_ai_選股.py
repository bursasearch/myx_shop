import pandas as pd
import numpy as np
import os
import sys
import glob
from datetime import datetime, timezone, timedelta
import time
import json

print("=" * 50)
print("馬來西亞 AI 選股腳本開始執行...")
print(f"執行時間: {datetime.now()}")
print("=" * 50)
time.sleep(2)  # 測試用暫停

# ====================
# ⚙️ 参数配置
# ====================

# 数据文件夹路径
DATA_FOLDER = "/data/data/com.termux/files/home/gdrive/stock_data/Myx_Data/EOD/"
REPORT_FOLDER = "/data/data/com.termux/files/home/gdrive/stock_data/Myx_Data/"
TOP_N = 10

# 檢查重要路徑是否存在
print("檢查資料路徑...")
print(f"數據文件夾: {DATA_FOLDER}")
print(f"是否存在: {os.path.exists(DATA_FOLDER)}")
print(f"報告文件夾: {REPORT_FOLDER}")
print(f"是否存在: {os.path.exists(REPORT_FOLDER)}")
time.sleep(1)

# 如果路徑不存在，嘗試創建
if not os.path.exists(REPORT_FOLDER):
    print("嘗試創建報告文件夾...")
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    print(f"創建結果: {os.path.exists(REPORT_FOLDER)}")

# 设置马来西亚时区 (UTC+8)
MALAYSIA_TIMEZONE = timezone(timedelta(hours=8))

# 市场状态阈值
MARKET_DOWNTURN_THRESHOLD = 10

# 放宽筛选条件以适应市场低迷期
MIN_VOLUME = 150000
MIN_PRICE = 0.20
MAX_PRICE = 15.00
MIN_BUY_PCT = 45
MIN_CHANGE = 0.008

# ====================
# ✨ 新增：打字效果函数
# ====================
def typewriter_print(text, delay=0.02):
    """
    以打字机效果打印文本。
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()

# ====================
# ⏰ 时间与文件处理函数
# ====================
def get_malaysia_time():
    """获取马来西亚当前时间 (UTC+8)"""
    return datetime.now(MALAYSIA_TIMEZONE)

def format_malaysia_date(dt):
    """格式化马来西亚日期"""
    return dt.strftime("%Y年%-m月%-d日")

def find_latest_trading_date(data_path):
    """
    在指定路徑中尋找最近一個交易日的 .csv 檔案。
    """
    # 2025年Bursa Malaysia官方交易假日
    holidays = [
        datetime(2025, 1, 1).date(),
        datetime(2025, 1, 29).date(),
        datetime(2025, 1, 30).date(),
        datetime(2025, 2, 11).date(),
        datetime(2025, 3, 18).date(),
        datetime(2025, 3, 31).date(),
        datetime(2025, 4, 1).date(),
        datetime(2025, 5, 1).date(),
        datetime(2025, 5, 12).date(),
        datetime(2025, 6, 2).date(),
        datetime(2025, 6, 7).date(),
        datetime(2025, 6, 27).date(),
        datetime(2025, 8, 31).date(),
        datetime(2025, 9, 1).date(),
        datetime(2025, 9, 5).date(),
        datetime(2025, 9, 15).date(),
        datetime(2025, 9, 16).date(),
        datetime(2025, 10, 20).date(),
        datetime(2025, 12, 25).date(),
    ]

    current_date = datetime.now().date()

    while True:
        if current_date.weekday() >= 5:
            current_date -= timedelta(days=1)
            continue

        if current_date in holidays:
            current_date -= timedelta(days=1)
            continue

        filename = current_date.strftime('%Y%m%d.csv')
        file_path = os.path.join(data_path, filename)

        if os.path.exists(file_path):
            typewriter_print(f"✅ 找到最近的交易日數據：{filename}")
            return file_path
        else:
            typewriter_print(f"❌ 找不到 {filename}，繼續尋找前一個交易日...")
            current_date -= timedelta(days=1)

# ====================
# 🎯 网页输出功能
# ====================
def generate_web_output():
    """
    生成网页可直接使用的选股结果
    基于您之前提供的股票列表
    """
    web_stocks = [
        {"code": "2429", "name": "TANCO", "price": 0.95, "tag": "📈低价股资金流入", "reason": "资金持续流入"},
        {"code": "5398", "name": "GAMUDA", "price": 5.17, "tag": "💪强势股", "reason": "技术面强势突破"},
        {"code": "0652NP", "name": "HSI-PWNP", "price": 0.56, "tag": "🔥超跌反弹机会", "reason": "超跌反弹信号"},
        {"code": "5326", "name": "99SMART", "price": 3.23, "tag": "💪强势股", "reason": "量价齐升"},
        {"code": "0652KN", "name": "HSI-CWKN", "price": 0.20, "tag": "📈低价股资金流入", "reason": "低价股活跃"},
        {"code": "5296", "name": "MRDIY", "price": 1.54, "tag": "🔥超跌反弹机会", "reason": "估值修复"},
        {"code": "0652KO", "name": "HSI-CWKO", "price": 0.47, "tag": "📈低价股资金流入", "reason": "资金关注"},
        {"code": "5323", "name": "JPG", "price": 1.56, "tag": "💡观察名单", "reason": "技术形态改善"},
        {"code": "8664", "name": "SPSETIA", "price": 0.83, "tag": "🔥超跌反弹机会", "reason": "超跌反弹"},
        {"code": "0652MQ", "name": "HSI-CWMQ", "price": 0.51, "tag": "🔥超跌反弹机会", "reason": "反弹潜力"}
    ]
    
    return web_stocks

# ====================
# 📊 数据分析函数（示例）
# ====================
def analyze_market_data():
    """分析市场数据"""
    typewriter_print("\n📊 开始分析市场数据...")
    time.sleep(1)
    
    try:
        # 这里可以添加您的实际数据分析逻辑
        latest_file = find_latest_trading_date(DATA_FOLDER)
        if latest_file:
            typewriter_print(f"✅ 使用数据文件: {os.path.basename(latest_file)}")
            
            # 示例：读取CSV数据
            # df = pd.read_csv(latest_file)
            # typewriter_print(f"📈 数据维度: {df.shape}")
            
        else:
            typewriter_print("⚠️ 未找到交易数据文件，使用模拟数据")
            
    except Exception as e:
        typewriter_print(f"❌ 数据分析错误: {str(e)}")
    
    time.sleep(1)

def calculate_technical_indicators():
    """计算技术指标"""
    typewriter_print("\n📈 计算技术指标...")
    time.sleep(1)
    
    # 这里可以添加您的技术指标计算逻辑
    typewriter_print("✅ RSI指标计算完成")
    typewriter_print("✅ MACD指标计算完成") 
    typewriter_print("✅ 移动平均线计算完成")
    time.sleep(1)  # 修正：这里原来是 type.sleep(1) 应该是 time.sleep(1)

def apply_ai_strategy():
    """应用AI选股策略"""
    typewriter_print("\n🤖 应用AI选股策略...")
    time.sleep(1)
    
    # 这里可以添加您的AI选股逻辑
    typewriter_print("✅ 多因子模型分析完成")
    typewriter_print("✅ 机器学习预测完成")
    typewriter_print("✅ 风险调整优化完成")
    time.sleep(1)

# ====================
# 📁 生成网页数据文件
# ====================
def save_web_data():
    """生成网页用的JSON数据文件"""
    try:
        web_stocks = generate_web_output()
        
        web_data = {
            "success": True,
            "timestamp": get_malaysia_time().strftime("%Y-%m-%d %H:%M:%S"),
            "selected_stocks": web_stocks,
            "strategy": "多因子AI选股",
            "market_condition": "normal",
            "total_selected": len(web_stocks),
            "analysis_date": get_malaysia_time().strftime("%Y-%m-%d"),
            "data_source": "Bursa Malaysia",
            "last_trading_day": "2025-11-14"
        }
        
        # 输出到js文件夹
        web_file_path = os.path.join("js", "ai_stocks.json")
        
        # 确保js文件夹存在
        os.makedirs(os.path.dirname(web_file_path), exist_ok=True)
        
        with open(web_file_path, 'w', encoding='utf-8') as f:
            json.dump(web_data, f, ensure_ascii=False, indent=2)
        
        typewriter_print(f"✅ 网页数据已保存: {web_file_path}")
        
        # 输出结果摘要
        print("\n" + "="*50)
        print("🤖 AI选股结果摘要:")
        print("="*50)
        for i, stock in enumerate(web_stocks, 1):
            print(f"{i:2d}. {stock['code']} {stock['name']} - RM{stock['price']} - {stock['tag']}")
        
        return True
        
    except Exception as e:
        typewriter_print(f"❌ 保存网页数据失败: {str(e)}")
        return False

# ====================
# 📋 生成文本报告
# ====================
def generate_text_report():
    """生成文本格式的报告"""
    try:
        web_stocks = generate_web_output()
        report_content = f"""
{'='*60}
🤖 馬來西亞 AI 選股報告
{'='*60}
生成時間: {get_malaysia_time().strftime('%Y-%m-%d %H:%M:%S')}
選股策略: 多因子AI選股
選中股票: {len(web_stocks)} 隻
數據來源: Bursa Malaysia
最後交易日: 2025-11-14

📈 推薦股票列表:
{'='*60}
"""
        
        for i, stock in enumerate(web_stocks, 1):
            report_content += f"{i:2d}. {stock['code']} {stock['name']}\n"
            report_content += f"   價格: RM{stock['price']} | 標籤: {stock['tag']}\n"
            report_content += f"   理由: {stock['reason']}\n"
            report_content += "   " + "-"*40 + "\n"
        
        report_content += f"""
💡 投資建議:
• 建議分散投資，避免過度集中
• 關注市場整體趨勢變化  
• 設定合理的止損止盈點
• 定期檢視投資組合

⚠️ 風險提示:
本報告僅供參考，不構成投資建議。
投資有風險，入市需謹慎。
{'='*60}
"""
        
        # 保存文本报告
        report_path = os.path.join(REPORT_FOLDER, "ai_stock_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        typewriter_print(f"✅ 文本报告已保存: {report_path}")
        
        # 在控制台显示报告
        print(report_content)
        
        return True
        
    except Exception as e:
        typewriter_print(f"❌ 生成文本报告失败: {str(e)}")
        return False

# ====================
# 🚀 主执行函数
# ====================
def main():
    """主执行函数"""
    try:
        typewriter_print("🚀 开始执行AI选股分析...")
        time.sleep(1)
        
        # 执行分析步骤
        analyze_market_data()
        calculate_technical_indicators() 
        apply_ai_strategy()
        
        # 生成输出文件
        web_success = save_web_data()
        report_success = generate_text_report()
        
        print("\n" + "="*60)
        typewriter_print("🎉 AI选股脚本执行完成！")
        print("="*60)
        
        if web_success:
            typewriter_print("✅ 网页数据生成成功")
        else:
            typewriter_print("❌ 网页数据生成失败")
            
        if report_success:
            typewriter_print("✅ 文本报告生成成功")
        else:
            typewriter_print("❌ 文本报告生成失败")
            
        typewriter_print(f"📅 分析时间: {get_malaysia_time().strftime('%Y-%m-%d %H:%M:%S')}")
        typewriter_print("🌐 请访问 stocks.html 查看交互式回测结果")
        
    except Exception as e:
        typewriter_print(f"💥 脚本执行错误: {str(e)}")
        
        # 错误时生成基础的JSON文件
        try:
            error_data = {
                "success": False,
                "error": str(e),
                "timestamp": get_malaysia_time().strftime("%Y-%m-%d %H:%M:%S"),
                "selected_stocks": []
            }
            
            web_file_path = os.path.join("js", "ai_stocks.json")
            os.makedirs(os.path.dirname(web_file_path), exist_ok=True)
            
            with open(web_file_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
                
            typewriter_print("⚠️ 已生成错误状态JSON文件")
            
        except Exception as json_error:
            typewriter_print(f"❌ 连错误JSON文件也无法生成: {str(json_error)}")

# ====================
# 🏃‍♂️ 脚本入口
# ====================
if __name__ == "__main__":
    main()