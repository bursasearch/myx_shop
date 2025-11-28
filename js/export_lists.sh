#!/bin/bash
# Export JSON product lists to CSV for Shopee, Lazada, Temu
# Keep original JSON files intact using cp

BASE="/data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop/js"

for platform in shopee lazada temu; do
  infile="$BASE/${platform}_lists.json"
  outfile="$BASE/${platform}_lists.csv"
  backup="$BASE/${platform}_lists.json.bak"

  if [ -f "$infile" ]; then
    # Make a backup copy of the original JSON
    cp "$infile" "$backup"

    (
      echo "id,name,price,stock,status,category,image,link,sales"
      jq -r '.products | sort_by(.id)[]
        | [.id, .name, .price, .stock, .status, .category, .image, .link, .sales]
        | @csv' "$infile"
    ) > "$outfile"

    echo "✅ Exported $platform → $outfile (backup saved as $backup)"
  else
    echo "⚠️ No JSON file found for $platform"
  fi
done
