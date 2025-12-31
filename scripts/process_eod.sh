#!/bin/bash
# 自动处理每日EOD数据并生成JSON

# 获取今天日期 (格式: YYYYMMDD)
TODAY=$(date +%Y%m%d)

# 输入CSV路径
CSV_PATH="/storage/emulated/0/eskay9761/stock_data/Myx_Data/EOD/${TODAY}.csv"

# 检查文件是否存在
if [ ! -f "$CSV_PATH" ]; then
  echo "❌ 未找到EOD文件: $CSV_PATH"
  exit 1
fi

# 运行生成器
python3 /storage/emulated/0/bursasearch/myx_shop/scripts/generate_json_from_eod_fixed_v2.py "$CSV_PATH"
