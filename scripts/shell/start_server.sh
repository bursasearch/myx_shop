#!/bin/bash

echo "🚀 启动股票回测服务器..."

cd ~/storage/shared/bursasearch/myx_shop

# 检查并杀死占用5050端口的进程
echo "检查端口5050..."
PID=$(lsof -ti:5050 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "发现占用进程 PID: $PID，正在停止..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# 检查Python进程
pkill -f "python.*api.py" 2>/dev/null

# 安装依赖（如果需要）
if [ -f "requirements.txt" ]; then
    echo "检查Python依赖..."
    pip install -r requirements.txt --user 2>/dev/null
fi

# 启动服务器
echo "启动Flask服务器..."
python api.py 2>&1 | tee server.log &

# 等待启动
sleep 5

# 测试服务器
echo "测试服务器连接..."
RESPONSE=$(curl -s http://127.0.0.1:5050/health 2>/dev/null || curl -s http://127.0.0.1:5000/health 2>/dev/null)

if echo "$RESPONSE" | grep -q "healthy"; then
    echo "✅ 服务器启动成功！"
    echo ""
    echo "🌐 访问链接:"
    echo "1. 股票回测: http://127.0.0.1:5050/retail-inv.html"
    echo "2. 主页面: http://127.0.0.1:5050/"
    echo "3. AI选股: http://127.0.0.1:5050/stocks.html"
    echo ""
    echo "📊 服务器日志: tail -f server.log"
else
    echo "❌ 服务器启动失败"
    echo "尝试备用端口 5000..."
    
    # 修改端口为5000
    sed -i "s/port=5050/port=5000/g" api.py 2>/dev/null
    sed -i "s/port=5050/port=5000/g" retail-inv.html 2>/dev/null
    
    pkill -f "python.*api.py" 2>/dev/null
    python api.py 2>&1 | tee server.log &
    sleep 5
    
    echo "🌐 尝试访问: http://127.0.0.1:5000/retail-inv.html"
fi

echo ""
echo "按 Ctrl+C 停止服务器"
wait
