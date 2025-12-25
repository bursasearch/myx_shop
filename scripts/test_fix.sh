#!/bin/bash
echo "=== 测试修复 ==="

INPUT_DIR="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD"
TEST_FILE="$INPUT_DIR/20251223.csv"
TEST_OUTPUT="test_fixed_output.csv"
TEST_AUDIT="test_fixed_audit.json"

echo "测试文件: $(basename "$TEST_FILE")"
echo ""

# 运行测试
python3 normalize_eod.py "$TEST_FILE" "$TEST_OUTPUT" "eod_config.json" "$TEST_AUDIT"

echo ""
echo "=== 测试结果 ==="

if [ -f "$TEST_OUTPUT" ]; then
    echo "1. 输出文件已创建"
    echo "2. 行数: $(wc -l < "$TEST_OUTPUT")"
    
    echo ""
    echo "3. 前3行数据:"
    head -4 "$TEST_OUTPUT" | column -t -s,
    
    echo ""
    echo "4. Chg列检查:"
    echo "   有值的行数: $(tail -n +2 "$TEST_OUTPUT" | cut -d',' -f7 | grep -vc '^-$' || echo "0")"
    echo "   示例值: $(tail -n +2 "$TEST_OUTPUT" | head -1 | cut -d',' -f7)"
    
    echo ""
    echo "5. Sector分布:"
    tail -n +2 "$TEST_OUTPUT" | cut -d',' -f3 | sort | uniq -c | sort -rn | head -5
    
    echo ""
    echo "6. 查看审计日志摘要:"
    if [ -f "$TEST_AUDIT" ]; then
        python3 -c "
import json
with open('$TEST_AUDIT', 'r') as f:
    audit = json.load(f)
print(f'输入行: {audit[\"rows_in\"]}')
print(f'输出行: {audit[\"rows_out\"]}')
print(f'Chg有值的行: {audit.get(\"chg_values_count\", {}).get(\"has_value\", 0)}')
sectors = audit.get(\"sector_distribution\", {})
print(f'Sector分布 (前5):')
for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]:
    percent = (count / audit[\"rows_out\"]) * 100
    print(f'  {sector}: {count} ({percent:.1f}%)')
"
    fi
else
    echo "输出文件未创建，检查错误信息"
fi
