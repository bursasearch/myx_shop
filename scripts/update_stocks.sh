#!/bin/bash

# 设置环境变量
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
export HOME=/data/data/com.termux/files/home

CHANNEL_ID="UC2hOpX6LsgisPRFH9vYSHXA"
RSS_URL="https://www.youtube.com/feeds/videos.xml?channel_id=$CHANNEL_ID"

HTML_FILE="$HOME/my-website/public/stocks.html"
LOG_FILE="$HOME/update_stocks.log"                
TMP_DIR="$HOME/.cache/rss"
mkdir -p "$TMP_DIR"
RSS_FILE="$TMP_DIR/youtube_rss.xml"
ID_FILE="$TMP_DIR/latest_ids.txt"

echo "$(date): 開始更新股票頁面" >> "$LOG_FILE"

# 检查 HTML 文件是否存在
if [ ! -f "$HTML_FILE" ]; then
    echo "$(date): 錯誤：HTML 文件不存在: $HTML_FILE" >> "$LOG_FILE"
    termux-notification --title "股票更新失敗" --content "HTML 文件不存在" 2>/dev/null || true
    exit 1
fi

# 备份原始文件
cp "$HTML_FILE" "$HTML_FILE.bak"

# 嘗試下載 RSS
echo "$(date): 下載 RSS: $RSS_URL" >> "$LOG_FILE"
curl -s -H "User-Agent: Mozilla/5.0" "$RSS_URL" -o "$RSS_FILE"
CURL_EXIT=$?
echo "$(date): curl exit code: $CURL_EXIT" >> "$LOG_FILE"

# 如果 curl 失敗，嘗試 wget
if [ ! -s "$RSS_FILE" ] || [ $CURL_EXIT -ne 0 ]; then
    echo "$(date): 嘗試使用 wget..." >> "$LOG_FILE"
    wget --quiet --user-agent="Mozilla/5.0" -O "$RSS_FILE" "$RSS_URL"
    WGET_EXIT=$?
    echo "$(date): wget exit code: $WGET_EXIT" >> "$LOG_FILE"
fi

# 檢查 RSS 是否下載成功
if [ ! -f "$RSS_FILE" ] || [ ! -s "$RSS_FILE" ]; then
    echo "$(date): RSS file missing or empty" >> "$LOG_FILE"
    echo "$(date): 錯誤：無法下載 RSS" >> "$LOG_FILE"
    termux-notification --title "股票更新失敗" --content "RSS 無法下載" 2>/dev/null || true
    # 恢复备份
    mv "$HTML_FILE.bak" "$HTML_FILE"
    exit 1
fi

# 检查 RSS 文件内容
echo "$(date): RSS 文件大小: $(wc -c < "$RSS_FILE") bytes" >> "$LOG_FILE"

# 抓 2 個 videoId
VIDEO1=$(grep -o '<yt:videoId>[^<]*</yt:videoId>' "$RSS_FILE" | head -1 | sed 's/<[^>]*>//g')
VIDEO2=$(grep -o '<yt:videoId>[^<]*</yt:videoId>' "$RSS_FILE" | head -2 | tail -1 | sed 's/<[^>]*>//g')

# 檢查是否抓到有效的 videoId
if [ -z "$VIDEO1" ] || [ -z "$VIDEO2" ]; then
    echo "$(date): 錯誤：無法解析影片 ID" >> "$LOG_FILE"
    echo "$(date): VIDEO1: $VIDEO1, VIDEO2: $VIDEO2" >> "$LOG_FILE"
    echo "$(date): RSS 前 500 字符:" >> "$LOG_FILE"
    head -c 500 "$RSS_FILE" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    termux-notification --title "股票更新失敗" --content "無法解析影片 ID" 2>/dev/null || true
    # 恢复备份
    mv "$HTML_FILE.bak" "$HTML_FILE"
    exit 1
fi

DATE1=$(date +"%Y年%m月%d日")
DATE2=$(date +"%Y年%m月%d日" --date="1 day ago")

echo "$(date): 找到影片: $VIDEO1, $VIDEO2" >> "$LOG_FILE"

# 更新 HTML - 使用临时文件避免原地修改问题
TMP_HTML="$TMP_DIR/stocks_temp.html"
cp "$HTML_FILE" "$TMP_HTML"

# 逐个替换 placeholder
sed -i "s|PLACEHOLDER1|$VIDEO1|g" "$TMP_HTML"
sed -i "s|PLACEHOLDER1_DATE|$DATE1|g" "$TMP_HTML"
sed -i "s|PLACEHOLDER2|$VIDEO2|g" "$TMP_HTML"
sed -i "s|PLACEHOLDER2_DATE|$DATE2|g" "$TMP_HTML"
sed -i "s|Last updated: .*|Last updated: $(date)|g" "$TMP_HTML"

# 检查替换是否成功
if grep -q "PLACEHOLDER" "$TMP_HTML"; then
    echo "$(date): 警告：仍有未替换的 PLACEHOLDER" >> "$LOG_FILE"
    grep "PLACEHOLDER" "$TMP_HTML" >> "$LOG_FILE"
fi

# 移动回原位置
mv "$TMP_HTML" "$HTML_FILE"

echo "$(date): 更新完成！最新影片: $VIDEO1, $VIDEO2" >> "$LOG_FILE"

# 重建 Hugo 网站
echo "$(date): 開始重建 Hugo..." >> "$LOG_FILE"
cd "$HOME/my-website" || exit 1
hugo
HUGO_EXIT=$?
echo "$(date): Hugo 重建完成，exit code: $HUGO_EXIT" >> "$LOG_FILE"

if [ $HUGO_EXIT -eq 0 ]; then
    termux-notification --title "股票更新成功" --content "最新: $VIDEO1" 2>/dev/null || true
else
    termux-notification --title "Hugo 重建失敗" --content "exit code: $HUGO_EXIT" 2>/dev/null || true
    # 恢复原始 HTML 文件
    mv "$HTML_FILE.bak" "$HTML_FILE"
fi

# 清理
rm -f "$RSS_FILE" "$ID_FILE" "$HTML_FILE.bak"

echo "$(date): 脚本执行完成" >> "$LOG_FILE"