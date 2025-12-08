#!/bin/bash
echo "📅 每日AI選股分析任務"
echo "開始時間: $(date)"

cd /storage/emulated/0/bursasearch/myx_shop/scripts

# 運行自動更新
./auto_update.sh

# 記錄日誌
echo "任務完成於: $(date)" >> update_log.txt
