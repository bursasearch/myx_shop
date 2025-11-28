#!/data/data/com.termux/files/usr/bin/bash

# Base path (adjust if needed)
BASE="/data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop/js"

SRC="$BASE/shopee_lists.json"
DEST_ADMIN="$BASE/Admin/shopee_lists.json"
DEST_STAFF="$BASE/Staff/shopee_lists.json"

# Check if source exists
if [ ! -f "$SRC" ]; then
  echo "❌ Source file not found: $SRC"
  exit 1
fi

# Copy to Admin
cp "$SRC" "$DEST_ADMIN" && echo "✅ Copied to Admin"

# Copy to Staff
cp "$SRC" "$DEST_STAFF" && echo "✅ Copied to Staff"

echo "🎯 Done: shopee_lists.json propagated to Admin and Staff"
