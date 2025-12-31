#!/bin/bash
# 备份和恢复原始脚本

cd /storage/emulated/0/bursasearch/myx_shop/scripts

echo "📁 脚本管理"
echo "=========="

case "$1" in
    backup)
        if [ -f "generate_json_from_eod.py" ]; then
            cp generate_json_from_eod.py generate_json_from_eod.py.backup
            echo "✅ 备份: generate_json_from_eod.py → generate_json_from_eod.py.backup"
        else
            echo "❌ 找不到原始脚本"
        fi
        ;;
    
    restore)
        if [ -f "generate_json_from_eod.py.backup" ]; then
            cp generate_json_from_eod.py.backup generate_json_from_eod.py
            echo "✅ 恢复: generate_json_from_eod.py.backup → generate_json_from_eod.py"
        else
            echo "❌ 找不到备份文件"
        fi
        ;;
    
    use-fixed)
        if [ -f "generate_json_from_eod_fixed_v2.py" ]; then
            cp generate_json_from_eod_fixed_v2.py generate_json_from_eod.py
            echo "✅ 使用修复版v2"
        else
            echo "❌ 找不到修复版v2"
        fi
        ;;
    
    use-original)
        if [ -f "generate_json_from_eod.py.backup" ]; then
            cp generate_json_from_eod.py.backup generate_json_from_eod.py
            echo "✅ 使用原始脚本"
        elif [ -f "generate_json_from_eod_original.py" ]; then
            cp generate_json_from_eod_original.py generate_json_from_eod.py
            echo "✅ 使用原始脚本"
        else
            echo "⚠️  找不到原始脚本，保持不变"
        fi
        ;;
    
    list)
        echo "📂 可用脚本:"
        ls -la generate_json_from_eod*.py 2>/dev/null
        echo ""
        echo "📂 备份文件:"
        ls -la *.backup 2>/dev/null
        ;;
    
    *)
        echo "用法: $0 [backup|restore|use-fixed|use-original|list]"
        echo ""
        echo "选项:"
        echo "  backup      - 备份当前脚本"
        echo "  restore     - 恢复备份的脚本"
        echo "  use-fixed   - 使用修复版v2"
        echo "  use-original - 使用原始脚本"
        echo "  list        - 列出所有脚本"
        ;;
esac
