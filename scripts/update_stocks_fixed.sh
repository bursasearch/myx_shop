#!/bin/bash

export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
export HOME=/data/data/com.termux/files/home

# 工作日检查
CURRENT_DAY=$(date +%u)
if [ "$CURRENT_DAY" -eq 6 ] || [ "$CURRENT_DAY" -eq 7 ]; then
    echo "$(date): 週末跳過更新" >> "$HOME/update_stocks.log"
    exit 0
fi

CHANNEL_ID="UC2hOpX6LsgisPRFH9vYSHXA"
RSS_URL="https://www.youtube.com/feeds/videos.xml?channel_id=$CHANNEL_ID"

LOG_FILE="$HOME/update_stocks.log"
TMP_DIR="$HOME/.cache/rss"
mkdir -p "$TMP_DIR"
RSS_FILE="$TMP_DIR/youtube_rss.xml"

echo "$(date): 開始更新股票頁面" >> "$LOG_FILE"

# 下载 RSS
curl -s -H "User-Agent: Mozilla/5.0" "$RSS_URL" -o "$RSS_FILE"

if [ ! -s "$RSS_FILE" ]; then
    echo "$(date): RSS 下載失敗" >> "$LOG_FILE"
    exit 1
fi

# 提取视频ID
VIDEO_IDS=($(grep -o '<yt:videoId>[^<]*</yt:videoId>' "$RSS_FILE" | sed 's/<[^>]*>//g' | head -2))

if [ ${#VIDEO_IDS[@]} -lt 2 ]; then
    echo "$(date): 無法獲取影片ID" >> "$LOG_FILE"
    exit 1
fi

VIDEO1="${VIDEO_IDS[0]}"
VIDEO2="${VIDEO_IDS[1]}"
DATE1=$(date +"%Y年%m月%d日")
DATE2=$(date +"%Y年%m月%d日" --date="1 day ago")

echo "$(date): 更新影片: $VIDEO1 ($DATE1), $VIDEO2 ($DATE2)" >> "$LOG_FILE"

# 更新布局文件 - 重要：先替换_DATE，再替换视频ID
LAYOUT_FILE="$HOME/my-website/layouts/_default/stocks.html"
if [ -f "$LAYOUT_FILE" ]; then
    # 创建临时文件
    TMP_FILE="$TMP_DIR/stocks_temp.html"
    
    # 正确的替换顺序：先日期，后视频ID
    sed "s|PLACEHOLDER1_DATE|$DATE1|g; s|PLACEHOLDER2_DATE|$DATE2|g; s|PLACEHOLDER1|$VIDEO1|g; s|PLACEHOLDER2|$VIDEO2|g" "$LAYOUT_FILE" > "$TMP_FILE"
    
    # 移动回原位置
    mv "$TMP_FILE" "$LAYOUT_FILE"
    
    echo "$(date): 已更新布局文件" >> "$LOG_FILE"
else
    echo "$(date): 錯誤：布局文件不存在" >> "$LOG_FILE"
    exit 1
fi

# 重建 Hugo
cd "$HOME/my-website"
hugo

echo "$(date): 更新完成" >> "$LOG_FILE"

# 清理
rm -f "$RSS_FILE"
