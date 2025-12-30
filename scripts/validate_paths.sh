#!/bin/bash
# validate_paths.sh
# Audit-safe pre-push check for image paths in HTML files

echo "🔍 Scanning HTML files for image path issues..."

# 1. Flag absolute paths (src starting with /)
bad_refs=$(grep -nR '<img[^>]*src="/' --include="*.html" .)

# 2. Flag missing relative paths (file not found in repo)
missing_refs=""
while IFS=: read -r file line content; do
    # Extract file path from src attribute
    src=$(echo "$content" | sed -n 's/.*src="\([^"]*\)".*/\1/p')
    if [ -n "$src" ]; then
        # Skip external URLs (http, https, data:)
        if [[ "$src" =~ ^http ]] || [[ "$src" =~ ^data: ]]; then
            continue
        fi
        # Check if file exists relative to repo root
        if [ ! -f "$src" ] && [ ! -f "$(dirname "$file")/$src" ]; then
            missing_refs+="$file → $src"$'\n'
        fi
    fi
done < <(grep -nR '<img[^>]*src="' --include="*.html" .)

# Report results
if [ -n "$bad_refs" ] || [ -n "$missing_refs" ]; then
    [ -n "$bad_refs" ] && {
        echo "❌ Found absolute image paths:"
        echo "$bad_refs"
    }
    [ -n "$missing_refs" ] && {
        echo "❌ Missing image files referenced in HTML:"
        echo "$missing_refs" | sort -u
    }
    echo "⚠️ Please fix these issues before pushing."
    exit 1
else
    echo "✅ No image path issues detected. Safe to push."
    exit 0
fi
