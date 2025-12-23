#!/data/data/com.termux/files/usr/bin/bash
# GitHub推送脚本
cd "/storage/emulated/0/bursasearch/myx_shop"
git add web/*.html web/*.json web/history/*.json
git commit -m "更新: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
