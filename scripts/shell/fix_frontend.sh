#!/bin/bash
echo "修复前端代码..."

# 备份
cp retail-inv.html retail-inv.html.bak

# 修复 fetch 调用
python3 -c "
import re

with open('retail-inv.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 fetch URL
content = re.sub(
    r'const response = await fetch\(\s*[\"\'][^\"\']*single-stock-backtest[\"\']',
    'const response = await fetch(\"/single-stock-backtest\"',
    content
)

# 确保 formData 正确
content = re.sub(
    r'const formData = \{.*?\}',
    '''const formData = {
            stock_code: document.getElementById('stock_code').value.trim(),
            start_date: document.getElementById('start_date').value,
            end_date: document.getElementById('end_date').value,
            initial_investment: parseFloat(document.getElementById('initial_investment').value)
        };''',
    content,
    flags=re.DOTALL
)

with open('retail-inv.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('修复完成')
"
