#!/data/data/com.termux/files/usr/bin/bash
# ===================================================
# for_rerail-inv_html.sh
# 安全版本 - 专为 Jota+ 和 Termux 优化
# 创建 Bursa Malaysia 项目结构和 HTML 页面
# ===================================================

set -e  # 遇到错误时立即停止

# 配置变量
PROJECT_DIR="/storage/emulated/0/bursasearch/myx_shop"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$PROJECT_DIR/setup_log_${TIMESTAMP}.txt"

# 颜色定义（用于更好看的输出）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_message() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# 检查存储权限
check_storage() {
    log_message "检查存储权限..."
    if [ -d "/storage/emulated/0" ]; then
        log_success "存储权限正常"
    else
        log_warning "未检测到存储权限，尝试设置..."
        termux-setup-storage || {
            log_error "请手动运行: termux-setup-storage"
        }
        sleep 2
    fi
}

# 创建目录结构
create_directories() {
    log_message "创建项目目录结构..."
    
    # 主项目目录
    mkdir -p "$PROJECT_DIR" || log_error "无法创建项目目录"
    cd "$PROJECT_DIR" || log_error "无法进入项目目录"
    
    # 子目录
    mkdir -p scripts
    mkdir -p auto_scripts
    mkdir -p web/history
    mkdir -p assets/css
    mkdir -p assets/js
    mkdir -p assets/images
    mkdir -p data/json
    mkdir -p logs
    mkdir -p backups
    
    log_success "目录结构创建完成"
}

# 创建 Python 脚本
create_python_scripts() {
    log_message "创建 Python 脚本..."
    
    # update_web_data.py
    cat > scripts/update_web_data.py << 'PYEOF1'
#!/usr/bin/env python3
"""
更新网页数据脚本
"""
import json
import datetime
import os

def main():
    print("🔄 更新网页数据...")
    
    # 这里可以添加实际的数据更新逻辑
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 示例：更新一个简单的状态文件
    status = {
        "last_updated": current_time,
        "status": "success",
        "message": "数据更新完成"
    }
    
    os.makedirs("data/json", exist_ok=True)
    with open("data/json/update_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 数据更新完成于 {current_time}")

if __name__ == "__main__":
    main()
PYEOF1

    # investment_calculator.py
    cat > scripts/investment_calculator.py << 'PYEOF2'
#!/usr/bin/env python3
"""
投资计算器脚本
"""
import json
import math

def calculate_investment(principal, rate, years):
    """
    计算复利投资回报
    """
    amount = principal * math.pow(1 + rate/100, years)
    profit = amount - principal
    return {
        "principal": principal,
        "rate": rate,
        "years": years,
        "final_amount": round(amount, 2),
        "total_profit": round(profit, 2),
        "annual_return": round(profit / years, 2)
    }

def main():
    print("💰 投资计算器")
    
    # 示例计算
    result = calculate_investment(10000, 8, 10)
    
    print(f"本金: RM {result['principal']:,.2f}")
    print(f"年利率: {result['rate']}%")
    print(f"投资年限: {result['years']} 年")
    print(f"最终金额: RM {result['final_amount']:,.2f}")
    print(f"总利润: RM {result['total_profit']:,.2f}")
    
    # 保存结果
    import os
    os.makedirs("data/json", exist_ok=True)
    with open("data/json/investment_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("✅ 计算结果已保存")

if __name__ == "__main__":
    main()
PYEOF2

    # eod_processor.py (简版)
    echo '#!/usr/bin/env python3
print("📊 EOD 数据处理脚本")
print("(实际逻辑需要根据数据源实现)")
' > scripts/eod_processor.py

    log_success "Python 脚本创建完成"
}

# 创建自动化脚本
create_automation_scripts() {
    log_message "创建自动化脚本..."
    
    # 更新所有数据
    cat > auto_scripts/update_all.sh << 'BASH1'
#!/data/data/com.termux/files/usr/bin/bash
# 完整更新流程
cd "/storage/emulated/0/bursasearch/myx_shop"
echo "🔄 $(date '+%Y-%m-%d %H:%M:%S') - 开始完整更新"
python3 scripts/eod_processor.py
python3 scripts/update_web_data.py
echo "✅ $(date '+%Y-%m-%d %H:%M:%S') - 更新完成"
BASH1

    # 更新网页数据
    cat > auto_scripts/update_web.sh << 'BASH2'
#!/data/data/com.termux/files/usr/bin/bash
# 仅更新网页数据
cd "/storage/emulated/0/bursasearch/myx_shop"
python3 scripts/update_web_data.py
BASH2

    # 运行投资计算器
    cat > auto_scripts/run_calculator.sh << 'BASH3'
#!/data/data/com.termux/files/usr/bin/bash
# 运行投资计算器
cd "/storage/emulated/0/bursasearch/myx_shop"
python3 scripts/investment_calculator.py
BASH3

    # 备份脚本
    cat > auto_scripts/backup_data.sh << 'BASH4'
#!/data/data/com.termux/files/usr/bin/bash
# 数据备份脚本
cd "/storage/emulated/0/bursasearch/myx_shop"
BACKUP_DIR="backups/backup_$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$BACKUP_DIR"
cp -r data "$BACKUP_DIR/"
cp -r web "$BACKUP_DIR/"
echo "✅ 数据已备份到: $BACKUP_DIR"
BASH4

    log_success "自动化脚本创建完成"
}

# 创建 HTML 页面
create_html_pages() {
    log_message "创建 HTML 页面..."
    
    # 主页面 (rerail-inv.html)
    cat > web/rerail-inv.html << 'HTML1'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bursa Malaysia - 投资分析</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #1a5f7a, #2a9d8f);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .btn {
            background-color: #2a9d8f;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #21867a;
        }
        .update-time {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Bursa Malaysia 投资分析</h1>
            <p>实时数据追踪与投资计算工具</p>
            <p class="update-time">最后更新: <span id="lastUpdate">加载中...</span></p>
        </div>
        
        <div class="data-grid">
            <div class="card">
                <h2>📊 股票数据</h2>
                <div id="stockData">加载数据中...</div>
                <button class="btn" onclick="updateStockData()">刷新数据</button>
            </div>
            
            <div class="card">
                <h2>💰 投资计算器</h2>
                <div>
                    <label>投资金额 (RM):</label>
                    <input type="number" id="principal" value="10000" style="width:100%;padding:8px;margin:10px 0;">
                    
                    <label>年利率 (%):</label>
                    <input type="number" id="rate" value="8" step="0.1" style="width:100%;padding:8px;margin:10px 0;">
                    
                    <label>投资年限:</label>
                    <input type="number" id="years" value="10" style="width:100%;padding:8px;margin:10px 0;">
                    
                    <button class="btn" onclick="calculateInvestment()">计算</button>
                </div>
                <div id="result" style="margin-top:20px;padding:15px;background:#f8f9fa;border-radius:5px;"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 数据图表</h2>
            <div id="chartContainer" style="height:300px;background:#f8f9fa;display:flex;align-items:center;justify-content:center;">
                图表区域 (可接入 Chart.js 或 ECharts)
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 工具</h2>
            <button class="btn" onclick="location.href='../auto_scripts/update_all.sh'">运行完整更新</button>
            <button class="btn" onclick="location.href='history.html'">查看历史数据</button>
            <button class="btn" onclick="backupData()">备份数据</button>
        </div>
    </div>
    
    <script src="../assets/js/main.js"></script>
    <script>
        // 加载更新时间
        fetch('../data/json/update_status.json')
            .then(response => response.json())
            .then(data => {
                document.getElementById('lastUpdate').textContent = data.last_updated || '未知';
            })
            .catch(err => {
                console.error('加载数据失败:', err);
                document.getElementById('lastUpdate').textContent = '加载失败';
            });
        
        function updateStockData() {
            alert('数据更新功能需要连接到后端API');
            // 这里可以添加实际的API调用
        }
        
        function calculateInvestment() {
            const principal = parseFloat(document.getElementById('principal').value);
            const rate = parseFloat(document.getElementById('rate').value);
            const years = parseInt(document.getElementById('years').value);
            
            // 简单计算
            const amount = principal * Math.pow(1 + rate/100, years);
            const profit = amount - principal;
            
            document.getElementById('result').innerHTML = `
                <strong>计算结果:</strong><br>
                本金: RM ${principal.toLocaleString()}<br>
                最终金额: RM ${amount.toLocaleString(undefined, {minimumFractionDigits: 2})}<br>
                总利润: RM ${profit.toLocaleString(undefined, {minimumFractionDigits: 2})}<br>
                年平均回报: RM ${(profit/years).toLocaleString(undefined, {minimumFractionDigits: 2})}
            `;
        }
        
        function backupData() {
            alert('备份功能需要后端支持');
        }
    </script>
</body>
</html>
HTML1

    # 历史数据页面
    cat > web/history.html << 'HTML2'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>历史数据 - Bursa Malaysia</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .history-item { 
            background: #f8f9fa; 
            padding: 15px; 
            margin: 10px 0; 
            border-left: 4px solid #2a9d8f;
            border-radius: 4px;
        }
        .date { color: #666; font-size: 14px; }
        .data { margin-top: 10px; }
    </style>
</head>
<body>
    <h1>📜 历史数据记录</h1>
    <a href="rerail-inv.html">← 返回主页面</a>
    
    <div id="historyList">
        <p>加载历史数据中...</p>
    </div>
    
    <script>
        // 示例历史数据
        const historyData = [
            { date: "2024-01-15", data: "KLCI: 1500.25点" },
            { date: "2024-01-14", data: "成交量: 3.2亿股" },
            { date: "2024-01-13", data: "热门股: MAYBANK, CIMB" }
        ];
        
        const container = document.getElementById('historyList');
        container.innerHTML = '';
        
        historyData.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <div class="date">📅 ${item.date}</div>
                <div class="data">${item.data}</div>
            `;
            container.appendChild(div);
        });
    </script>
</body>
</html>
HTML2

    log_success "HTML 页面创建完成"
}

# 设置权限
set_permissions() {
    log_message "设置脚本权限..."
    
    chmod +x scripts/*.py 2>/dev/null || true
    chmod +x auto_scripts/*.sh 2>/dev/null || true
    
    # 设置便捷命令别名
    cd ~
    rm -f bursa_update bursa_calc 2>/dev/null || true
    ln -sf "$PROJECT_DIR/auto_scripts/update_all.sh" ~/bursa_update
    ln -sf "$PROJECT_DIR/auto_scripts/run_calculator.sh" ~/bursa_calc
    
    log_success "权限设置完成"
}

# 验证安装
verify_installation() {
    log_message "验证安装结果..."
    
    echo "📁 项目结构:"
    tree "$PROJECT_DIR" -L 2 2>/dev/null || find "$PROJECT_DIR" -type f | head -20
    
    echo ""
    echo "📋 创建的文件:"
    find "$PROJECT_DIR" -type f -name "*.py" -o -name "*.sh" -o -name "*.html" | sort
    
    echo ""
    log_success "验证完成"
}

# 显示使用说明
show_instructions() {
    echo ""
    echo "="*60
    echo "🎉 安装完成！"
    echo "="*60
    echo ""
    echo "📁 项目目录: $PROJECT_DIR"
    echo "🌐 主页面: $PROJECT_DIR/web/rerail-inv.html"
    echo ""
    echo "🚀 快捷命令:"
    echo "  bursa_update    - 更新所有数据"
    echo "  bursa_calc      - 运行投资计算器"
    echo ""
    echo "📝 手动运行:"
    echo "  cd $PROJECT_DIR"
    echo "  python3 scripts/update_web_data.py"
    echo "  bash auto_scripts/backup_data.sh"
    echo ""
    echo "📊 查看日志: cat $LOG_FILE"
    echo "="*60
}

# 主执行函数
main() {
    clear
    echo "🚀 开始执行 for_rerail-inv_html.sh"
    echo "⏰ 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 执行步骤
    check_storage
    create_directories
    create_python_scripts
    create_automation_scripts
    create_html_pages
    set_permissions
    verify_installation
    show_instructions
    
    log_success "脚本执行完毕！"
}

# 执行主函数
main "$@"
