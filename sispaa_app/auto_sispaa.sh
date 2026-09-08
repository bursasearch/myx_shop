#!/bin/bash

echo "🔄 SISPAA 自动处理系统"
echo "========================"
echo ""

cd /storage/emulated/0/bursasearch/myx_shop/sispaa_app/

case "$1" in
    watch)
        echo "👀 监控模式: 将截图放入 jpg/ 目录"
        python3 ocr_to_csv.py watch
        ;;
    once)
        echo "📸 处理 jpg/ 目录下所有图片..."
        python3 ocr_to_csv.py all
        ;;
    *)
        echo ""
        echo "用法:"
        echo "  ./auto_sispaa.sh watch   # 监控模式（自动处理新图片）"
        echo "  ./auto_sispaa.sh once    # 批量处理已有图片"
        echo ""
        ;;
esac
